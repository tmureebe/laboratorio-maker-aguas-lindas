import { chromium } from 'playwright-chromium'
import { mkdirSync, writeFileSync, readFileSync, readdirSync, existsSync } from 'node:fs'
import { resolve } from 'node:path'
import assert from 'node:assert/strict'
import { serve } from './servir.mjs'

if(process.argv.includes('--backup')) { await import('./validar-backup.mjs'); process.exit(0) }

const root=resolve('..'), out=resolve(root,'04-exportacoes'), audit=resolve(root,'00-planejamento/auditoria')
mkdirSync(`${out}/slides`,{recursive:true});mkdirSync(audit,{recursive:true})
const quick=process.argv.includes('--quick'), makePdf=process.argv.includes('--pdf')
let server, base=process.env.MAKER_URL
if(!base){const started=await serve(`${out}/web`,0);server=started.server;base=started.url}
const report={url:base,compiled:true,externalRequests:[],consoleErrors:[],failedResponses:[],slides:[],interactions:[],date:new Date().toISOString()}
const browser=await chromium.launch({executablePath:process.env.CHROME_PATH||'/usr/bin/google-chrome',headless:true,args:['--enable-unsafe-swiftshader','--use-gl=angle','--use-angle=swiftshader','--mute-audio']})
try {
const context=await browser.newContext({viewport:{width:1920,height:1080},deviceScaleFactor:1,locale:'pt-BR',timezoneId:'America/Sao_Paulo'})
await context.route('**/*',route=>{
  const url=route.request().url()
  if(url.startsWith(base)||url.startsWith('data:')||url.startsWith('blob:'))return route.continue()
  report.externalRequests.push(url);return route.abort()
})
const page=await context.newPage()
const active=page.locator('.slidev-layout.maker:visible')
page.on('pageerror',error=>report.consoleErrors.push(String(error)))
page.on('response',response=>{if(response.status()>=400)report.failedResponses.push({url:response.url(),status:response.status()})})
async function go(n,clicks=0){
  await page.goto(`${base}/${n}${clicks?`?clicks=${clicks}`:''}`,{waitUntil:'networkidle'})
  await active.first().waitFor()
  await page.evaluate(()=>document.fonts.ready)
  if(n===12||n===16)await active.locator('.data-metrics button').first().waitFor()
  if(n===18)await page.waitForFunction(()=>document.querySelector('.model-canvas')?.getAttribute('data-ready')==='true'||document.querySelector('.model-hint')?.textContent?.includes('estática'))
  await page.addStyleTag({content:'.slidev-nav-controls, .slidev-nav, [data-slidev-no-print] { visibility:hidden!important }'})
  await page.mouse.move(1905,8)
  await page.waitForTimeout(160)
}
for(const n of quick?[1,3,12,13,17,18,20,25]:Array.from({length:25},(_,i)=>i+1)){
  await go(n,n===17?4:0)
  const metrics=await page.evaluate(()=>{
    const visible=e=>{const r=e.getBoundingClientRect();return r.width>0&&r.height>0&&r.right>0&&r.left<innerWidth&&r.bottom>0&&r.top<innerHeight&&getComputedStyle(e).visibility!=='hidden'}
    const slides=[...document.querySelectorAll('.slidev-layout.maker')].filter(visible)
    const layout=slides.find(e=>{const r=e.getBoundingClientRect();return Math.abs(r.left)<5})||slides[0]
    const box=layout?.getBoundingClientRect(),content=layout?.querySelector('.slide-content')?.getBoundingClientRect()
    const issues=[]
    for(const el of layout?.querySelectorAll('h1,h2,h3,p,li,td,.person,.card,.sensor-dashboard,.model-viewer,.photo,.video-card,pre')||[]){
      if(!visible(el))continue
      const r=el.getBoundingClientRect()
      if(content&&(r.right>content.right+3||r.left<content.left-3||r.bottom>content.bottom+5)&&!layout.classList.contains('cover'))issues.push({tag:el.tagName,cls:el.className,text:el.textContent?.slice(0,90),bounds:[Math.round(r.left),Math.round(r.top),Math.round(r.right),Math.round(r.bottom)],limit:[content.right,content.bottom]})
      if(el.tagName==='PRE'&&el.scrollWidth>el.clientWidth+3&&!['auto','scroll'].includes(getComputedStyle(el).overflowX))issues.push({tag:'PRE',message:'Código cortado sem rolagem horizontal',scrollWidth:el.scrollWidth,clientWidth:el.clientWidth})
    }
    const broken=[...layout.querySelectorAll('img')].filter(e=>visible(e)&&(!e.complete||e.naturalWidth===0)).map(e=>e.getAttribute('src'))
    const links=[...layout.querySelectorAll('a[href]')].map(e=>{const r=e.getBoundingClientRect();return{href:e.href,x:r.x,y:r.y,width:r.width,height:r.height}})
    const videos=[...layout.querySelectorAll('video')].map(e=>{const r=e.getBoundingClientRect();return{src:e.getAttribute('src'),poster:e.getAttribute('poster'),label:e.getAttribute('aria-label'),x:r.x,y:r.y,width:r.width,height:r.height}})
    return{title:layout.querySelector('h1')?.textContent,footer:layout.querySelector('footer')?.textContent,issues,broken,links,videos,layout:[box?.width,box?.height]}
  })
  await page.screenshot({path:`${out}/slides/${String(n).padStart(2,'0')}.jpg`,type:'jpeg',quality:95,animations:'disabled'})
  report.slides.push({number:n,...metrics})
  console.log(`Slide ${String(n).padStart(2,'0')}: ${metrics.title?.replaceAll('\n',' ')} | ${metrics.issues.length} transbordamentos, ${metrics.broken.length} imagens ausentes`)
}
if(!quick){
  await go(1);await page.keyboard.press('ArrowRight');await page.waitForURL(/\/2(?:\?|$)/);await page.keyboard.press('ArrowLeft');await page.waitForURL(/\/1(?:\?|$)/)
  report.interactions.push('Navegação por teclado: avançar e voltar')
  await go(17);const codeBefore=await active.locator('pre').first().innerHTML();await page.keyboard.press('ArrowRight');await page.waitForTimeout(250);const codeAfter=await active.locator('pre').first().innerHTML();assert.notEqual(codeBefore,codeAfter)
  report.interactions.push('Destaque progressivo de linhas do código')
  const code=active.locator('.code-grid pre').first()
  const expectedCode=readFileSync('./exemplos/estacao-completo.ino','utf8').trimEnd()
  assert.equal((await code.textContent()).trimEnd(),expectedCode,'O bloco exibe o firmware completo, sem omitir linhas')
  assert.equal(await code.locator('code > .line').count(),319,'Todas as 319 linhas estão presentes')
  await page.waitForFunction(()=>{
    const pre=document.querySelector('.slidev-layout.maker .code-grid pre')
    const line=pre?.querySelectorAll('code > .line')[138]
    if(!line)return false
    const box=pre.getBoundingClientRect(),target=line.getBoundingClientRect()
    return target.top>=box.top&&target.bottom<=box.bottom
  })
  report.interactions.push('Firmware completo: 319 linhas conferidas com a cópia preparada; destaque navega até a linha 139')
  await code.hover();await page.mouse.wheel(0,600)
  await page.waitForFunction(()=>document.querySelector('.slidev-layout.maker .code-grid pre')?.scrollTop>0)
  const scroll=await code.evaluate(el=>{
    el.scrollTop=el.scrollHeight;el.scrollLeft=el.scrollWidth
    return{top:el.scrollTop,left:el.scrollLeft,height:el.scrollHeight-el.clientHeight,width:el.scrollWidth-el.clientWidth}
  })
  assert(scroll.top>0&&Math.abs(scroll.top-scroll.height)<=1,'Rolagem alcança a última linha')
  assert.equal(scroll.width,0,'Todas as linhas cabem na largura do código, sem rolagem horizontal')
  assert.equal(scroll.left,0,'O código não precisa de deslocamento horizontal')
  assert(new URL(page.url()).pathname.endsWith('/17'),'Rolar o código mantém o slide 17')
  for(const viewport of [{width:1280,height:720},{width:1440,height:900}]){
    await page.setViewportSize(viewport)
    const dimensions=await code.evaluate(el=>({width:el.clientWidth,contentWidth:el.scrollWidth,vertical:getComputedStyle(el).overflowY}))
    assert.equal(dimensions.contentWidth,dimensions.width,`Código sem transbordamento horizontal em ${viewport.width} × ${viewport.height}`)
    assert.equal(dimensions.vertical,'scroll','Barra de rolagem vertical mantida')
  }
  await page.setViewportSize({width:1920,height:1080})
  report.interactions.push('Código: rolagem vertical com mouse até a última linha; sem transbordamento horizontal em 1920 × 1080, 1280 × 720 e 1440 × 900')
  for(const [n,dataset] of [[12,'estacao'],[16,'colmeia']]){
    await go(n)
    const original=JSON.parse(readFileSync(`public/dados/${dataset}.json`,'utf8'))
    assert((await active.locator('.data-caption').innerText()).includes(original.total.toLocaleString('pt-BR')))
    const initial=await active.locator('.data-metrics button').first().innerText()
    const initialPath=await active.locator('.sensor-chart > path').getAttribute('d')
    for(const button of await active.locator('.data-metrics button').all()){await button.click();assert.equal(await button.getAttribute('aria-pressed'),'true')}
    if(dataset==='colmeia'){
      const audio=active.getByRole('button',{name:/Nível de áudio/})
      assert.equal(await audio.getAttribute('aria-pressed'),'true')
      const lastAudio=original.registros.at(-1).audio.toLocaleString('pt-BR',{minimumFractionDigits:1,maximumFractionDigits:1})
      assert((await audio.innerText()).includes(`${lastAudio} dBFS`),'Cartão de áudio exibe o valor do arquivo e a unidade dBFS')
      assert.notEqual(await active.locator('.sensor-chart > path').getAttribute('d'),initialPath,'Selecionar áudio troca a série do gráfico')
      assert((await active.locator('.sensor-chart').getAttribute('aria-label')).includes('Nível de áudio'))
      assert.equal(await active.getByRole('button',{name:/Bateria/}).count(),0)
      await page.mouse.move(1905,8)
      await page.screenshot({path:`${audit}/slide-16-audio.png`,animations:'disabled'})
      report.interactions.push('Áudio da colmeia: leitura final conferida com o arquivo local, unidade dBFS e histórico selecionável no lugar da bateria')
    }
    await active.locator('.data-toolbar select').selectOption('ultimo')
    const lastDay=original.registros.at(-1).data.slice(0,10),count=original.registros.filter(r=>r.data.startsWith(lastDay)).length
    assert((await active.locator('.data-caption').innerText()).includes(count.toLocaleString('pt-BR')))
    const graph=await active.locator('.sensor-chart').boundingBox();await page.mouse.move(graph.x+graph.width*.35,graph.y+100)
    assert((await active.locator('.data-caption').innerText()).includes('Medição selecionada'))
    report.interactions.push(`Dados ${dataset}: ${original.total} registros, métricas, filtro do último dia (${count}), cursor; valor inicial ${initial.replaceAll('\n',' ')}`)
  }
  await go(18)
  for(const [i,id] of ['colmeia-caixa','estacao-caixa','calorimetro','piramides-prisma'].entries()){
    await active.locator('#model-choice').selectOption(String(i))
    await page.waitForTimeout(300)
    await page.waitForFunction(()=>document.querySelector('.model-canvas')?.getAttribute('data-ready')==='true')
    const canvas=active.locator('.model-canvas canvas'), before=await canvas.evaluate(e=>e.toDataURL())
    await page.getByRole('button',{name:'Girar modelo',exact:true}).click()
    const after=await canvas.evaluate(e=>e.toDataURL());assert.notEqual(before,after)
    await page.getByRole('button',{name:'Aproximar modelo',exact:true}).click();await page.getByRole('button',{name:'Afastar modelo',exact:true}).click();await page.getByRole('button',{name:'Enquadrar modelo',exact:true}).click()
    await canvas.screenshot({path:`${audit}/modelo-${id}.png`})
    report.interactions.push(`GLB ${id}: carregamento, rotação, zoom e enquadramento`)
  }
  for(const n of [13,15]){
    await go(n)
    for(const video of await active.locator('video').all()){
      const info=await video.evaluate(async v=>{
        if(v.readyState<1)await new Promise((resolve,reject)=>{v.addEventListener('loadedmetadata',resolve,{once:true});v.addEventListener('error',reject,{once:true})})
        v.muted=true;await v.play();return{src:v.getAttribute('src'),duration:v.duration,controls:v.controls,codec:v.canPlayType('video/mp4; codecs="avc1.42E01E, mp4a.40.2"')}
      })
      await page.waitForTimeout(500);assert(await video.evaluate(v=>v.currentTime>0));assert(info.controls);assert(info.duration>0)
      await video.evaluate(v=>{v.currentTime=v.duration/2});await page.waitForTimeout(200);await video.evaluate(v=>v.pause())
      report.interactions.push(`Vídeo ${info.src}: duração ${info.duration.toFixed(2)}s, controles, reprodução e busca; codec ${info.codec}`)
    }
    await active.locator('video').first().evaluate(v=>{window.__makerTestVideo=v;v.play()})
    await page.evaluate(()=>document.activeElement?.blur());await page.keyboard.press('ArrowDown');await page.waitForTimeout(300)
    assert(await page.evaluate(()=>window.__makerTestVideo.paused));report.interactions.push(`Vídeo do slide ${n} pausa ao navegar`)
  }
  const range=await context.request.get(`${base}/videos/colmeia-apiario.mp4`,{headers:{Range:'bytes=0-1023'}});assert.equal(range.status(),206);assert.equal((await range.body()).length,1024)
  report.interactions.push('Servidor: requisição parcial de vídeo (HTTP 206)')
  await page.route('**/*.glb',route=>route.abort())
  await go(18);assert(await active.locator('.model-fallback').isVisible());assert((await active.locator('.model-hint').innerText()).includes('estática'))
  report.interactions.push('Falha de carregamento 3D: imagem local de contingência exibida')
  await page.unroute('**/*.glb')
  const publicFiles=[]
  function walk(dir){for(const f of readdirSync(dir,{withFileTypes:true})){if(f.isDirectory())walk(`${dir}/${f.name}`);else publicFiles.push(`${dir}/${f.name}`)}}walk('public')
  for(const file of publicFiles){const response=await context.request.head(`${base}/${file.slice(7)}`);assert.equal(response.status(),200,file)}
  report.interactions.push(`Todos os ${publicFiles.length} recursos de public retornam HTTP 200 na versão compilada`)
}
writeFileSync(`${audit}/${quick?'revisao-preliminar':'validacao'}.json`,JSON.stringify(report,null,2))
if(makePdf){
  assert.equal(report.slides.length,25,'PDF exige captura de todos os slides')
  const pages=report.slides.map(slide=>{
    const image=readFileSync(`${out}/slides/${String(slide.number).padStart(2,'0')}.jpg`).toString('base64')
    const links=slide.links.filter(l=>l.href.startsWith('https://')).map(l=>`<a href="${l.href}" style="left:${l.x}px;top:${l.y}px;width:${l.width}px;height:${l.height}px"></a>`).join('')
    return `<section><img src="data:image/jpeg;base64,${image}" alt="Slide ${slide.number}">${links}</section>`
  }).join('')
  await page.goto('about:blank')
  await page.setContent(`<!doctype html><html lang="pt-BR"><head><title>Laboratório Maker do IFG — Visita CNPq — 15/09/2026</title><style>@page{size:1920px 1080px;margin:0}*{box-sizing:border-box}body{margin:0}section{position:relative;width:1920px;height:1080px;break-after:page}section:last-child{break-after:auto}img{width:1920px;height:1080px;display:block}a{position:absolute;display:block}</style></head><body>${pages}</body></html>`,{waitUntil:'load'})
  await page.pdf({path:`${out}/laboratorio-maker-ifg-cnpq-2026.pdf`,width:'1920px',height:'1080px',printBackground:true,preferCSSPageSize:true,margin:{top:0,right:0,bottom:0,left:0}})
  console.log('PDF de contingência gerado a partir das 25 capturas da versão compilada.')
}
const issues=report.slides.reduce((n,s)=>n+s.issues.length+s.broken.length,0)+report.consoleErrors.length+report.failedResponses.length+report.externalRequests.length
console.log(JSON.stringify({slides:report.slides.length,interactions:report.interactions.length,issues,externalRequests:report.externalRequests.length,consoleErrors:report.consoleErrors.length,failedResponses:report.failedResponses.length},null,2))
if(issues&&!quick)process.exitCode=1
} finally {await browser.close();server?.close()}
