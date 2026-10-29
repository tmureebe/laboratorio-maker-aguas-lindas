/* Local educational application. All grading is deterministic JavaScript. */
(() => {
'use strict';
const C=window.COURSE, K=window.CourseCore, BANK=window.BANK, F=window.FIRMWARE;
const KEY='colmeia-curso-v1';
const $=(s,root=document)=>root.querySelector(s);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const defaults=()=>({version:1,answers:{},drafts:{},reflections:{},visited:[],route:'home',training:{},trainingId:null,session:null,bankHistory:[],previousBank:[],outline:{},sim:K.newSimulation()});
let storageProblem='', state=defaults();
try{const raw=localStorage.getItem(KEY);if(raw){const parsed=JSON.parse(raw);if(parsed.version!==1)throw Error('version');state=restore(parsed);}}catch{storageProblem='Não foi possível recuperar o progresso salvo. Você pode continuar; exporte uma cópia ao terminar.';}
function restore(data){
  if(!data||typeof data!=='object'||Array.isArray(data)||data.version!==1)throw Error('Formato de progresso inválido.');
  const s=defaults();
  const object=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
  const response=x=>object(x)?{text:typeof x.text==='string'?x.text.slice(0,30000):'',spoken:x.spoken===true,reviewed:x.reviewed===true,...(['rever','apoio','seguro'].includes(x.rating)?{rating:x.rating}:{})}:{};
  if(object(data.answers))for(const q of C.modules.flatMap(m=>m.activities)){const a=data.answers[q.id];if(object(a)&&q.type!=='reflect')s.answers[q.id]={value:a.value,correct:K.grade(q,a.value),attempts:Number.isInteger(a.attempts)&&a.attempts>0?a.attempts:1,firstCorrect:a.firstCorrect===true};}
  if(object(data.drafts))s.drafts=data.drafts;
  if(object(data.reflections))for(const q of C.modules.flatMap(m=>m.activities).filter(q=>q.type==='reflect'))if(object(data.reflections[q.id]))s.reflections[q.id]=response(data.reflections[q.id]);
  if(object(data.training))for(const q of BANK)if(object(data.training[q.id]))s.training[q.id]=response(data.training[q.id]);
  if(object(data.outline))for(const [key,value] of Object.entries(data.outline))if(typeof value==='string')s.outline[key]=value.slice(0,30000);
  s.visited=Array.isArray(data.visited)?data.visited.filter(x=>C.modules.some(m=>m.id===x)):[];
  s.route=typeof data.route==='string'?data.route:'home';
  s.trainingId=BANK.some(q=>q.id===data.trainingId)?data.trainingId:null;
  s.previousBank=Array.isArray(data.previousBank)?data.previousBank.filter(id=>BANK.some(q=>q.id===id)):[];
  s.bankHistory=Array.isArray(data.bankHistory)?data.bankHistory.filter(x=>x&&Array.isArray(x.ids)).slice(-30):[];
  const b=data.session;
  if(b&&Array.isArray(b.ids)&&b.ids.length&&b.ids.every(id=>BANK.some(q=>q.id===id))&&Number.isFinite(b.deadline)&&Number.isFinite(b.started)&&b.responses&&typeof b.responses==='object'){
    s.session={...b,index:Math.max(0,Math.min(Number(b.index)||0,b.ids.length-1)),responses:Object.fromEntries(b.ids.map(id=>[id,response(b.responses[id])])),done:!!b.done};
  }
  if(data.sim&&['now','queue','history','events','lost','boot','secondsSince','lastSleep'].every(k=>Number.isFinite(data.sim[k])&&data.sim[k]>=0)&&data.sim.queue<=2016&&(data.sim.next===null||Number.isFinite(data.sim.next)))s.sim={...K.newSimulation(),...data.sim};
  return s;
}
function save(){
  try{localStorage.setItem(KEY,JSON.stringify(state));$('#save-status').textContent='Progresso salvo neste navegador';}
  catch{$('#save-status').textContent='Não foi possível salvar neste navegador';storageProblem='O navegador bloqueou o salvamento ou ficou sem espaço. Seu trabalho atual continua disponível nesta aba; exporte o progresso em Meu progresso.';showNotice(storageProblem);}
  updateProgress();
}
function showNotice(text){const node=$('#notice');node.textContent=text;node.hidden=!text;}
function updateProgress(){const done=C.modules.filter(m=>K.moduleDone(m,state)).length;$('#global-progress').textContent=`${done}/${C.modules.length} módulos · Meu progresso`;}
const moduleIndex=id=>C.modules.findIndex(m=>m.id===id);
const clockText=minute=>`${String(Math.floor(minute%1440/60)).padStart(2,'0')}:${String(Math.floor(minute%60)).padStart(2,'0')}`;
const timerText=secs=>`${String(Math.floor(secs/60)).padStart(2,'0')}:${String(secs%60).padStart(2,'0')}`;
const tag=text=>`<span class="tag">${esc(text)}</span>`;
function lead(kicker,title,description){return `<div class="page-lead"><p class="eyebrow">${esc(kicker)}</p><h1>${esc(title)}</h1><p class="intro">${esc(description)}</p></div>`;}
function nav(route){
  $('#navigation').innerHTML=`<div class="nav-section"><a class="${route==='home'?'active':''}" href="#home"><span aria-hidden="true">⌂</span> Minha trilha</a><a class="${route==='simulator'?'active':''}" href="#simulator"><span aria-hidden="true">↻</span> Laboratório</a><a class="${route==='code'?'active':''}" href="#code"><span aria-hidden="true">{ }</span> Código do projeto</a><a class="${route==='bank'?'active':''}" href="#bank"><span aria-hidden="true">◉</span> Modo banca</a><a class="${route==='progress'?'active':''}" href="#progress"><span aria-hidden="true">▥</span> Meu progresso</a></div><p class="nav-label">A TRILHA · ${C.modules.length} MÓDULOS</p><div class="module-nav">${C.modules.map((m,i)=>`<a href="#lesson/${m.id}" class="${location.hash.includes('/'+m.id)?'active':''}"><span class="nav-number">${K.moduleDone(m,state)?'✓':String(i+1).padStart(2,'0')}</span><span>${esc(m.title)}${K.moduleDone(m,state)?'<small>Concluído</small>':''}</span></a>`).join('')}</div>`;
  $$('.nav-section a.active,.module-nav a.active').forEach(a=>a.setAttribute('aria-current','page'));
}
function $$(s,root=document){return [...root.querySelectorAll(s)];}
let orderDrafts={}, simPlan=null, simStep=-1, simCommitted=false, codeQuery='',bankFilter='all';
function route(){
  const parts=location.hash.slice(1).split('/');const section=parts[0]||'home';
  state.route=location.hash.slice(1)||'home';
  if(section==='lesson'&&moduleIndex(parts[1])>=0&&!state.visited.includes(parts[1]))state.visited.push(parts[1]);
  nav(section);document.body.classList.remove('menu-open');$('#menu-toggle').setAttribute('aria-expanded','false');$('#menu-toggle').textContent='Abrir menu';
  const renderers={home:renderHome,lesson:()=>renderLesson(parts[1],parts[2]||'learn'),simulator:renderSimulator,code:()=>renderCode(parts[1]),bank:()=>renderBank(parts[1]||'train'),progress:renderProgress};
  (renderers[section]||renderHome)();
  save();tick();
  $('#main').focus({preventScroll:true});window.scrollTo(0,0);
}
function renderHome(){
  const next=C.modules.find(m=>!K.moduleDone(m,state))||C.modules[0];
  $('#main').innerHTML=`<section class="hero"><div><p class="eyebrow">UMA TRILHA PARA ENTENDER E EXPLICAR</p><h1>Entenda a colmeia.<br><em>Conte a história<br>do projeto.</em></h1><p class="intro">Do primeiro sensor às perguntas da banca. Explore o sistema, experimente decisões e aprenda a encontrar as respostas no código.</p><a class="button" href="#lesson/${next.id}">${state.visited.length?'Continuar minha trilha':'Começar pelo projeto'} <span aria-hidden="true">→</span></a><p class="fine">14 módulos · no seu ritmo · progresso salvo no navegador</p></div><div class="hero-visual"><p class="eyebrow">O CAMINHO DOS DADOS</p>${hardwareMarkup('home')}<p class="fine">Toque nos componentes para descobrir seu papel.</p></div></section><section class="section-head"><div><p class="eyebrow">APRENDER, EXPERIMENTAR, EXPLICAR</p><h2>Sua trilha de aprendizagem</h2></div><a href="#progress">Ver desempenho →</a></section><div class="module-grid">${C.modules.map((m,i)=>`<a class="module-card ${K.moduleDone(m,state)?'complete':''}" href="#lesson/${m.id}"><div class="card-top"><span class="module-number">${String(i+1).padStart(2,'0')}</span>${tag(K.moduleDone(m,state)?'Concluído':m.level)}</div><h3>${esc(m.title)}</h3><p>${esc(m.subtitle)}</p><div class="card-bottom"><span>≈ ${m.minutes} min · ${m.activities.length} atividades</span><span aria-hidden="true">↗</span></div></a>`).join('')}</div><section class="callout split"><div><p class="eyebrow">QUANDO QUISER PRATICAR</p><h2>Uma banca. Cinco minutos.<br>Suas próprias palavras.</h2><p>Treine sem pressa ou responda a uma rodada sorteada. Compare sua explicação com os conceitos essenciais.</p></div><a class="button secondary" href="#bank">Explorar o modo banca →</a></section>`;
}
const components={
  dht:{name:'DHT11',detail:'Dois sensores: temperatura e umidade interna e externa. GPIO 4 e 21.',ref:'readDHTSensors'},
  lid:{name:'MC-38',detail:'Contato magnético da tampa no GPIO 27. Na montagem prevista, HIGH indica aberto.',ref:'readLidSensor'},
  esp:{name:'ESP32',detail:'Executa o firmware e coordena leitura, processamento, armazenamento, comunicação e sono.',ref:'setup'},
  battery:{name:'Alimentação',detail:'O divisor reduz a tensão de +SYS para leitura no GPIO 34. A carga é estimada pela tensão.',ref:'readBattery'},
  mic:{name:'INMP441',detail:'Microfone digital via I2S. O programa extrai indicadores; não envia uma gravação.',ref:'readAudioFeatures'},
  cloud:{name:'Memória e banco',detail:'A fila fica na flash com LittleFS. A rede leva lotes ao Firebase nos momentos permitidos.',ref:'uploadQueuedReadings'}
};
function hardwareMarkup(id){return `<div class="hardware-map" data-map="${id}">${Object.entries(components).map(([key,c])=>`<button class="component ${key==='esp'?'board':''}" data-component="${key}" aria-pressed="false"><span aria-hidden="true">${{dht:'°C',lid:'⌑',esp:'ESP32',battery:'±',mic:'∿',cloud:'▤'}[key]}</span><strong>${esc(c.name)}</strong>${key==='esp'?'<small>coordena o ciclo</small>':''}</button>`).join('')}</div><div class="component-detail" aria-live="polite">Selecione um componente para ver sua função no sistema.</div>`;}
function renderLesson(id,tab){
  const m=C.modules.find(x=>x.id===id);if(!m){renderHome();return;}
  const i=moduleIndex(id),done=K.moduleDone(m,state);
  let content='';
  if(tab==='practice')content=`<div class="section-head"><div><h2>Agora é com você</h2><p>Responda, confira a explicação e tente novamente se precisar. Nas respostas abertas, você faz a comparação.</p></div></div>${m.activities.map(renderQuestion).join('')}`;
  else if(tab==='code')content=`<section class="card"><p class="eyebrow">PRIMEIRO, A IDEIA</p><h2>Em palavras simples</h2><pre class="pseudo">${esc(m.pseudo)}</pre></section><section class="card"><h2>Depois, o firmware</h2><p>${m.refs.length?'Abra uma tarefa por vez. Observe o que entra, o que ela faz e o que sai.':'Neste módulo, a prioridade é explicar a visão geral. Você pode explorar o arquivo completo quando quiser.'}</p><div class="ref-grid">${m.refs.map(name=>`<button class="ref-card" data-code="${name}"><code>${esc(name)}${F.functions.some(f=>f.name===name)?'()':''}</code><span>${esc(C.explanations[name]||'Ver esta parte do firmware.')}</span><strong>Abrir trecho →</strong></button>`).join('')}</div><a href="#code">Consultar o firmware completo →</a></section>`;
  else content=`<section class="objectives"><h2>Ao final, você consegue…</h2><ul>${m.goals.map(g=>`<li>${esc(g)}</li>`).join('')}</ul></section><div class="reading">${m.blocks.map((b,j)=>`<section class="lesson-block"><span class="block-number">${String(j+1).padStart(2,'0')}</span><div><h2>${esc(b.title)}</h2><p>${b.text}</p></div></section>`).join('')}</div>${labMarkup(m.lab)}<aside class="takeaway"><strong>Guarde esta ideia</strong><p>${esc(m.summary)}</p></aside>`;
  $('#main').innerHTML=`<div class="breadcrumb"><a href="#home">Minha trilha</a><span>/</span><span>Módulo ${i+1} de ${C.modules.length}</span>${done?tag('Concluído'):''}</div>${lead(m.level,m.title,m.subtitle)}<nav class="tabs" aria-label="Etapas do módulo"><a class="${tab==='learn'?'selected':''}" href="#lesson/${id}/learn">1. Entenda</a><a class="${tab==='code'?'selected':''}" href="#lesson/${id}/code">2. Veja no código</a><a class="${tab==='practice'?'selected':''}" href="#lesson/${id}/practice">3. Pratique</a></nav>${content}<div class="lesson-footer"><a class="button secondary" href="${i?'#lesson/'+C.modules[i-1].id:'#home'}">← ${i?'Módulo anterior':'Minha trilha'}</a>${tab!=='practice'?`<a class="button" href="#lesson/${id}/${tab==='learn'?'code':'practice'}">${tab==='learn'?'Ver no código':'Praticar'} →</a>`:`<a class="button" href="${i<C.modules.length-1?'#lesson/'+C.modules[i+1].id:'#bank'}">${i<C.modules.length-1?'Próximo módulo':'Ir para a banca'} →</a>`}</div>`;
  $$('.tabs .selected').forEach(a=>a.setAttribute('aria-current','page'));
  updateLabs();
}
function findQ(id){for(const m of C.modules){const q=m.activities.find(q=>q.id===id);if(q)return q;}return null;}
function renderQuestion(q){
  const saved=state.answers[q.id], draft=state.drafts[q.id]??saved?.value;
  let controls='';
  if(q.type==='reflect'){
    const r=state.reflections[q.id]||{};
    return `<section class="activity reflection" id="q-${q.id}"><div class="activity-meta">EXPLIQUE COM SUAS PALAVRAS ${tag('Autoavaliação')}</div><h3>${esc(q.prompt)}</h3><label for="text-${q.id}">Sua resposta</label><textarea id="text-${q.id}" data-reflect-text="${q.id}" placeholder="Escreva sua explicação antes de comparar…">${esc(r.text||'')}</textarea><label class="check"><input type="checkbox" data-reflect-spoken="${q.id}" ${r.spoken?'checked':''}> Respondi em voz alta</label><button data-reflect-review="${q.id}">Comparar com a resposta-modelo</button><div class="feedback" id="feedback-${q.id}" aria-live="polite">${r.reviewed?reflectionFeedback(q):''}</div></section>`;
  }
  if(['choice','tf','predict','line','locate'].includes(q.type))controls=`<fieldset><legend class="sr-only">${esc(q.prompt)}</legend>${q.options.map((o,i)=>`<label class="option"><input type="radio" name="answer" value="${i}" ${String(draft)===String(i)?'checked':''}><span>${['line','locate'].includes(q.type)?'<code>'+esc(o)+'</code>':esc(o)}</span></label>`).join('')}</fieldset>`;
  if(['fill','edit'].includes(q.type))controls=`<pre class="pseudo">${esc(q.code)}</pre><label for="answer-${q.id}">${q.type==='edit'?'Sua alteração':'Complete a lacuna'}</label><input id="answer-${q.id}" name="answer" type="text" value="${esc(draft||'')}" autocomplete="off" spellcheck="false" required>`;
  if(q.type==='match')controls=`<div class="match-list">${q.pairs.map((p,i)=>`<label>${esc(p[0])}<select name="pair-${i}" required><option value="">Escolha a correspondência</option>${[...q.pairs].map(p=>p[1]).sort((a,b)=>a.localeCompare(b,'pt')).map(v=>`<option ${draft?.[i]===v?'selected':''} value="${esc(v)}">${esc(v)}</option>`).join('')}</select></label>`).join('')}</div>`;
  if(q.type==='order'){
    let values=Array.isArray(draft)&&draft.length===q.items.length&&new Set(draft.map(Number)).size===q.items.length&&draft.every(v=>Number.isInteger(Number(v))&&v>=0&&v<q.items.length)?draft.map(Number):null;
    if(!values){values=K.shuffle(q.items.map((_,i)=>i));if(values.every((v,i)=>v===i))values.reverse();}
    orderDrafts[q.id]=values;
    controls=`<p class="fine">Use as setas para colocar a primeira etapa no topo.</p><ol class="order-list">${values.map((v,i)=>`<li><span>${esc(q.items[v])}</span><div><button type="button" class="icon-button" data-order="${q.id}" data-position="${i}" data-direction="-1" ${i===0?'disabled':''} aria-label="Mover ${esc(q.items[v])} para cima">↑</button><button type="button" class="icon-button" data-order="${q.id}" data-position="${i}" data-direction="1" ${i===values.length-1?'disabled':''} aria-label="Mover ${esc(q.items[v])} para baixo">↓</button></div></li>`).join('')}</ol>`;
  }
  const typeNames={choice:'Múltipla escolha',tf:'Verdadeiro ou falso',predict:'Preveja o resultado',line:'Selecione a linha',locate:'Localize a função',fill:'Complete o código',edit:'Altere um trecho',match:'Faça as associações',order:'Ordene as etapas'};
  return `<section class="activity" id="q-${q.id}"><div class="activity-meta">${esc(typeNames[q.type])} ${tag(C.topics[q.topic])}</div><h3>${esc(q.prompt)}</h3><form data-question="${q.id}">${controls}<button type="submit">Conferir resposta</button></form><div id="feedback-${q.id}" class="feedback" aria-live="polite">${saved?(JSON.stringify(draft)!==JSON.stringify(saved.value)?'Resposta alterada. Confira novamente para atualizar o resultado.':questionFeedback(q,K.grade(q,saved.value))):''}</div></section>`;
}
function questionFeedback(q,correct){return `<div class="result ${correct?'success':'retry'}"><strong>${correct?'Isso mesmo.':'Vamos revisar.'}</strong><p>${esc(q.why)}</p>${!correct?'<small>Ajuste sua resposta e confira novamente. O resultado mais recente aparece no progresso.</small>':''}</div>`;}
function reflectionFeedback(q){return `<div class="result model"><strong>Uma resposta possível</strong><p>${esc(q.model)}</p><strong>Conceitos para conferir na sua explicação</strong><div class="chips">${q.concepts.split(';').map(x=>tag(x.trim())).join('')}</div><p class="fine">Prática registrada. Seu texto não recebeu uma nota automática.</p></div>`;}
function readAnswer(form,q){if(q.type==='match')return q.pairs.map((_,i)=>form.elements['pair-'+i].value);if(q.type==='order')return [...orderDrafts[q.id]];return new FormData(form).get('answer');}
function labMarkup(lab){
  if(!lab)return '';
  const head='<p class="eyebrow">EXPERIMENTE</p>';
  if(lab==='hardware')return `<section class="card lab">${head}<h2>Conheça as conexões</h2>${hardwareMarkup('lesson')}</section>`;
  if(lab==='flow')return `<section class="card lab split"><div>${head}<h2>Leve uma hipótese ao laboratório</h2><p>Simule uma coleta sem rede, acompanhe a fila e veja o envio numa tentativa posterior. Cada etapa aponta para uma função real.</p></div><a class="button" href="#simulator">Abrir laboratório →</a></section>`;
  if(lab==='condition')return `<section class="card lab">${head}<h2>Uma condição muda o caminho</h2><div class="lab-controls"><label class="check"><input type="checkbox" id="condition-lid"> Tampa está aberta</label><label class="check"><input type="checkbox" id="condition-wake"> Despertou pela tampa</label><label class="check"><input type="checkbox" id="condition-day" checked> Janela diurna aberta</label></div><div id="condition-result" class="lab-result" aria-live="polite"></div><p class="fine">Estado atual da tampa e causa do despertar são independentes. Permissão para evento ainda depende de conexão e resposta do serviço.</p></section>`;
  if(lab==='battery')return `<section class="card lab">${head}<h2>A tensão vira uma estimativa</h2><label for="battery-value">Tensão reconstruída de +SYS (V)</label><input id="battery-value" type="range" min="3" max="4.4" step="0.01" value="3.8"><div id="battery-result" class="lab-result" aria-live="polite"></div><p class="fine">Modelo linear do firmware: 3,20 V → 0%; 4,15 V → 100%. Uma bateria real não precisa seguir uma relação linear entre tensão e energia restante.</p></section>`;
  if(lab==='audio')return `<section class="card lab">${head}<h2>Uma onda, dois controles</h2><div class="form-grid"><label>Amplitude digital<input id="audio-amplitude" type="range" min="0.05" max="1" step="0.05" value="0.5"></label><label>Frequência da onda simples (Hz)<input id="audio-frequency" type="range" min="100" max="800" step="50" value="200"></label></div><svg id="audio-wave" viewBox="0 0 640 140" role="img" aria-label="Onda senoidal sintética; a altura representa amplitude e a repetição representa frequência"></svg><div id="audio-result" class="lab-result" aria-live="polite"></div><p class="fine">Exemplo matemático de senoide pura, sem som reproduzido e sem acesso ao microfone. Para essa onda simples, frequência e cruzamentos se relacionam; isso não se generaliza a sons complexos.</p></section>`;
  if(lab==='outline')return `<section class="card lab">${head}<h2>Seu roteiro de apresentação</h2><p>Escreva lembretes com suas palavras. Registre apenas resultados e contribuições reais.</p>${[['objetivo','Qual problema o projeto investiga?'],['componentes','Quais componentes e grandezas você vai apresentar?'],['fluxo','Como vai explicar o caminho de uma medição?'],['evidencias','Quais resultados foram efetivamente observados?'],['limites','Quais limites e próximos testes devem ser mencionados?']].map(([id,label])=>`<label class="outline-label">${label}<textarea data-outline="${id}">${esc(state.outline[id]||'')}</textarea></label>`).join('')}<button data-print class="secondary">Imprimir roteiro e módulo</button></section>`;
  return '';
}
function updateLabs(){
  if($('#condition-result')){const lid=$('#condition-lid').checked,wake=$('#condition-wake').checked,day=$('#condition-day').checked;$('#condition-result').innerHTML=`<div><strong>lidOpen = ${lid}</strong><span>Sono: ${lid?60:600} s · EXT0 ${lid?'não habilitado':'habilitado'}</span></div><div><strong>${wake} && ${day} = ${wake&&day}</strong><span>Evento ${wake&&day?'permitido':'não permitido'} pela combinação de causa e janela.</span></div>`;}
  if($('#battery-result')){const v=Number($('#battery-value').value),pct=Math.max(0,Math.min(100,100*(v-3.2)/(4.15-3.2)));$('#battery-result').innerHTML=`<div><strong>${v.toFixed(2)} V</strong><span>No pino: ≈ ${(v/2).toFixed(2)} V</span></div><div><strong>${pct.toFixed(1)}%</strong><span>Estimativa limitada a 0–100%</span></div><progress value="${pct}" max="100" aria-label="Percentual estimado"></progress>`;}
  if($('#audio-result')){const a=Number($('#audio-amplitude').value),f=Number($('#audio-frequency').value),r=a/Math.sqrt(2),db=20*Math.log10(r);let points=[];for(let x=0;x<=640;x+=2)points.push(`${x},${70-Math.sin(x/640*0.02*f*2*Math.PI)*a*58}`);$('#audio-wave').innerHTML=`<path d="M0 70H640" class="wave-axis"/><polyline points="${points.join(' ')}" class="wave-line"/>`;$('#audio-result').innerHTML=`<div><strong>${a.toFixed(2)}</strong><span>Amplitude</span></div><div><strong>${r.toFixed(3)}</strong><span>RMS teórico</span></div><div><strong>${db.toFixed(1)} dBFS</strong><span>Nível digital</span></div><div><strong>${f} Hz</strong><span>Senoide de exemplo</span></div>`;}
}
function snippet(name){const custom={pinos:{start:61,end:75},intervalos:{start:94,end:110}};return F.functions.find(f=>f.name===name)||custom[name];}
function codeLines(start,end,interactive=false){return F.lines.slice(start-1,end).map((line,i)=>{const n=start+i;return interactive?`<button class="code-line" id="L${n}" data-source-line="${n}" title="Explicar a linha ${n}"><span class="line-number">${n}</span><code>${esc(line)||' '}</code></button>`:`<div class="code-line"><span class="line-number">${n}</span><code>${esc(line)||' '}</code></div>`;}).join('');}
function explanationForLine(n){return F.functions.find(f=>n>=f.start&&n<=f.end)?.name||(n>=61&&n<=75?'pinos':n>=94&&n<=110?'intervalos':null);}
function openCode(name){
  const s=snippet(name);if(!s)return;
  $('#dialog-title').textContent=name+(F.functions.some(f=>f.name===name)?'()':'');
  $('#dialog-body').innerHTML=`<p>${esc(C.explanations[name]||'Observe o que esta função recebe, quais decisões toma e o que retorna. Procure sua chamada no fluxo principal.')}</p><p class="fine">Trecho real sanitizado · linhas ${s.start}–${s.end} · ${name==='setup'?'Este é o fluxo completo; comece pelas chamadas principais.':''}</p><div class="source-code compact">${codeLines(s.start,s.end)}</div><a class="button secondary" href="#code/${name}" data-dialog-link>Ver no arquivo completo →</a>`;
  $('#code-dialog').showModal();
}
function renderCode(name){
  const target=snippet(name);const functions=F.functions;
  $('#main').innerHTML=`${lead('CONSULTA GUIADA','O firmware, por partes','Procure uma função ou uma expressão. Clique nas linhas para relacionar o trecho à sua finalidade.')}<div class="notice-inline">${esc(F.notice)} <a href="firmware-pedagogico.ino" download>Baixar cópia pedagógica</a></div><div class="code-tools"><label>Buscar no código<input id="code-search" type="search" value="${esc(codeQuery)}" placeholder="Ex.: lidOpen, SLEEP_INTERVAL_SECONDS"></label><label>Ir para uma função<select id="function-jump"><option value="">Selecione…</option>${['pinos','intervalos',...functions.map(f=>f.name)].map(n=>`<option value="${n}" ${n===name?'selected':''}>${n}</option>`).join('')}</select></label><button id="search-prev" class="secondary" aria-label="Ocorrência anterior">↑</button><button id="search-next" class="secondary" aria-label="Próxima ocorrência">↓</button></div><p id="search-status" class="fine" aria-live="polite">${F.lines.length} linhas · ${functions.length} funções</p><div class="code-layout"><div class="source-code full" id="code-scroll" tabindex="0" aria-label="Código com linhas numeradas">${codeLines(1,F.lines.length,true)}</div><aside class="code-explanation card" id="line-explanation"><p class="eyebrow">COMO LER</p><h2>Uma tarefa de cada vez</h2><p>Selecione uma função ou clique numa linha. Comece por readLidSensor(), depois explore setup().</p><p class="fine">Comentários descrevem intenção; condições e chamadas mostram o comportamento. A cópia preserva a lógica do original.</p></aside></div>`;
  if(target)selectLine(target.start,true);
  if(codeQuery)searchCode();
}
let searchMatches=[],searchIndex=-1;
function selectLine(n,scroll=false){
  $$('.code-line.selected').forEach(e=>e.classList.remove('selected'));const line=$('#L'+n);if(!line)return;
  line.classList.add('selected');
  const name=explanationForLine(n);const detail=name?C.explanations[name]:null;
  $('#line-explanation').innerHTML=`<p class="eyebrow">LINHA ${n}</p><h2>${esc(name?name+(F.functions.some(f=>f.name===name)?'()':''):'Contexto do arquivo')}</h2><p>${esc(detail||'Este trecho contém declarações, configuração ou uma função auxiliar. Observe nomes, tipos e comentários, e relacione-os à função principal que usa esses valores.')}</p>${name?`<button class="secondary" data-code="${name}">Abrir trecho explicado</button>`:''}`;
  if(scroll){const box=$('#code-scroll');box.scrollTop=line.offsetTop-box.offsetTop-50;}
}
function searchCode(){
  codeQuery=$('#code-search').value;const query=codeQuery.toLowerCase().trim();
  $$('.code-line.match').forEach(e=>e.classList.remove('match'));
  searchMatches=query?F.lines.map((line,i)=>line.toLowerCase().includes(query)?i+1:0).filter(Boolean):[];searchIndex=searchMatches.length?0:-1;
  searchMatches.forEach(n=>$('#L'+n).classList.add('match'));showMatch();
}
function showMatch(){if(searchIndex>=0)selectLine(searchMatches[searchIndex],true);$('#search-status').textContent=codeQuery?`${searchMatches.length} ocorrência(s)${searchMatches.length?' · '+(searchIndex+1)+' de '+searchMatches.length:''}`:`${F.lines.length} linhas · ${F.functions.length} funções`;}
function renderSimulator(){
  simPlan=null;simStep=-1;simCommitted=false;
  const s=state.sim;
  $('#main').innerHTML=`${lead('LABORATÓRIO INTERATIVO','Acompanhe uma coleta','Mude uma condição, faça uma previsão e percorra as decisões do programa. Os dados são fictícios e nenhum hardware ou banco é acessado.')}<div class="sim-layout"><section class="card sim-controls"><h2>Prepare o cenário</h2><label>Cenário inicial<select id="sim-preset"><option value="custom">Personalizar</option><option value="normal">Tentativa diurna normal</option><option value="offline">Wi-Fi indisponível às 08h</option><option value="night">Tampa abre às 02h</option><option value="daylid">Tampa abre às 09h, entre envios</option><option value="unknown">Liga às 02h sem relógio</option><option value="sensor">Falha do DHT11 externo</option><option value="full">Fila cheia e sem rede</option><option value="storage">Falha de gravação local</option></select></label><form id="sim-form"><fieldset id="sim-fields"><legend class="sr-only">Condições da simulação</legend><div class="form-grid"><label>Horário local do ciclo<input id="sim-time" type="time" value="${clockText(s.now)}" required></label><label>Causa do despertar<select id="sim-cause"><option value="timer">Temporizador</option><option value="lid">Tampa (EXT0)</option><option value="power">Inicialização/reset</option></select></label></div><label>Sono regular <output id="interval-output">10 minutos</output><input id="sim-interval" type="range" min="1" max="60" value="10" step="1"></label><div class="switch-list">${[['wifi','Wi-Fi disponível',true],['storage','Gravação local funciona',true],['sensor','DHT11 externo funciona',true],['firebase','Firebase confirma envios',true],['clock','Relógio já é válido',s.clock],['ntp','NTP consegue ajustar a hora',true],['lid','Tampa está aberta agora',false]].map(([id,label,on])=>`<label class="check"><input id="sim-${id}" type="checkbox" ${on?'checked':''}>${label}</label>`).join('')}</div><button type="submit">Iniciar ciclo passo a passo →</button></fieldset></form><div class="button-stack"><button id="sim-later" class="secondary">Ir à próxima tentativa com rede</button><button id="sim-reset" class="text-button">Reiniciar laboratório</button></div><details><summary>O que esta simulação simplifica?</summary><p>Usa contagens de fichas e resultados fictícios. Assume relógio sem deriva, 10 s fixos de trabalho por ciclo e sucesso integral de latest e remoção após um histórico confirmado. Não emula circuito, I2S, falhas parciais de arquivo ou latência da rede. O tempo de trabalho real varia. Somente ciclos concluídos ficam salvos; sair antes descarta o percurso em andamento. A fila conserva o limite de 2016 e os lotes, de 12.</p></details></section><section class="sim-stage"><div class="sim-metrics" id="sim-metrics"></div><div class="flow-rail" id="flow-rail" aria-label="Etapas do ciclo"></div><div class="card step-card" id="step-card" aria-live="polite"><p class="eyebrow">ANTES DE COMEÇAR</p><h2>Qual caminho você espera?</h2><p>Observe horário, causa do despertar e disponibilidade da rede. A medição será enviada, ficará na fila ou poderá ser perdida?</p><p>No firmware real, a decisão de Wi-Fi e a consulta de hora podem preceder a gravação. O percurso aqui segue essa ordem.</p></div><div class="step-controls"><button id="sim-prev" class="secondary" disabled>← Etapa anterior</button><button id="sim-next" disabled>Próxima etapa →</button><button id="sim-all" class="text-button" disabled>Ver o ciclo completo</button></div><div class="card"><div class="section-head"><h2>A fila local</h2><span id="queue-count"></span></div><div id="queue-visual" class="queue-visual"></div><p class="fine">Cada ficha visual representa uma medição. Acima de 24, mostramos uma amostra da fila.</p><div id="sim-reading"></div></div><div id="sim-summary" aria-live="polite"></div></section></div>`;
  updateSimView();
}
function simOptions(){const [h,m]=$('#sim-time').value.split(':').map(Number);if(!Number.isFinite(h)||!Number.isFinite(m))return null;const o={now:Math.floor(state.sim.now/1440)*1440+h*60+m,cause:$('#sim-cause').value,interval:Number($('#sim-interval').value)*60};for(const key of ['wifi','storage','sensor','firebase','clock','ntp','lid'])o[key]=$('#sim-'+key).checked;return o;}
function startSim(){const o=simOptions();if(!o)return;simPlan=K.simulateCycle(state.sim,o);simStep=0;simCommitted=false;$('#sim-fields').disabled=true;$('#sim-preset').disabled=true;updateSimView();}
function finishSim(){if(!simCommitted&&simPlan){state.sim=simPlan.state;simCommitted=true;save();$('#sim-fields').disabled=false;$('#sim-preset').disabled=false;$('#sim-time').value=clockText(state.sim.now);$('#sim-clock').checked=state.sim.clock;}}
function updateSimView(){
  const snapshot=simPlan?simPlan.steps[simStep].snapshot:state.sim;
  $('#sim-metrics').innerHTML=[['Na fila',snapshot.queue],['No histórico',snapshot.history],['Eventos',snapshot.events],['Perdas',snapshot.lost]].map(([label,n])=>`<div><span>${label}</span><strong>${n}</strong></div>`).join('');
  const labels=['Acorda','Identifica motivo','Inicializa','Lê sensores','Processa','Wi-Fi e horário','Armazena','Envia','Agenda','Dorme'];
  $('#flow-rail').innerHTML=labels.map((label,i)=>`<button class="flow-step ${simPlan&&i===simStep?'current':''} ${simPlan&&i<simStep?'past':''}" data-sim-step="${i}" ${!simPlan||(!simCommitted&&i>simStep)?'disabled':''} ${simPlan&&i===simStep?'aria-current="step"':''}><span>${i+1}</span>${label}</button>`).join('');
  if(simPlan){const step=simPlan.steps[simStep];$('#step-card').innerHTML=`<p class="eyebrow">ETAPA ${simStep+1} DE ${simPlan.steps.length}</p><h2>${esc(step.label)}</h2><p>${esc(step.detail)}</p><button class="code-link" data-code="${step.ref}"><code>${esc(step.ref)}()</code> · ver no firmware →</button>`;}
  $('#sim-prev').disabled=!simPlan||simStep===0;$('#sim-next').disabled=!simPlan||simStep===9;$('#sim-all').disabled=!simPlan||simStep===9;
  $('#queue-count').textContent=`${snapshot.queue} / 2016 fichas`;
  $('#queue-visual').innerHTML=snapshot.queue?Array.from({length:Math.min(24,snapshot.queue)},(_,i)=>`<span class="queue-ticket" aria-label="Ficha ${i+1}">▤</span>`).join('')+(snapshot.queue>24?`<span>+ ${snapshot.queue-24}</span>`:''):'<span class="muted">Fila vazia</span>';
  $('#sim-reading').innerHTML=simPlan&&simStep>=6?`<details><summary>Ver campos da ficha deste ciclo</summary><pre>${esc(JSON.stringify(simPlan.reading,null,2))}</pre><p class="fine">Representação simplificada. Temperatura e umidade são fictícias; null indica falha.</p></details>`:'';
  $('#sim-summary').innerHTML=simCommitted?`<div class="result success"><strong>Ciclo concluído e guardado no laboratório.</strong><p>Próximo despertar simulado: ${clockText(state.sim.now)}. Próxima tentativa periódica: ${state.sim.next===null?'depende de obter o horário':clockText(state.sim.next)+(state.sim.next>=Math.floor(state.sim.now/1440)*1440+1440?' no dia seguinte':'')}.</p><p>Experimente outro ciclo ou use “Ir à próxima tentativa com rede” para observar o envio posterior.</p></div>`:'';
}
function presetSim(name){
  let s=K.newSimulation();s.queue=state.sim.queue;s.history=state.sim.history;s.events=state.sim.events;s.lost=state.sim.lost;
  const o={wifi:true,storage:true,sensor:true,firebase:true,clock:true,ntp:true,lid:false,cause:'timer',time:'08:00'};
  if(name==='offline')o.wifi=false;
  if(name==='night'){o.time='02:00';o.cause='lid';o.lid=true;s.next=360;}
  if(name==='daylid'){o.time='09:00';o.cause='lid';o.lid=true;s.next=600;}
  if(name==='unknown'){o.time='02:00';o.clock=false;o.cause='power';s.next=null;}
  if(name==='sensor')o.sensor=false;
  if(name==='full'){o.wifi=false;s.queue=2016;}
  if(name==='storage')o.storage=false;
  if(name==='custom')return;
  const [h,m]=o.time.split(':').map(Number);s.now=h*60+m;s.clock=o.clock;state.sim=s;save();simPlan=null;simStep=-1;simCommitted=false;
  $('#sim-time').value=o.time;$('#sim-cause').value=o.cause;for(const k of ['wifi','storage','sensor','firebase','clock','ntp','lid'])$('#sim-'+k).checked=o[k];updateSimView();
}
function renderBank(mode){
  $('#main').innerHTML=`${lead('PREPARE SUA EXPLICAÇÃO','Modo banca','Pratique respostas curtas, relacione ideias ao código e reconheça o que ainda precisa ser medido.')}<nav class="tabs" aria-label="Modos da banca"><a class="${mode==='train'?'selected':''}" href="#bank/train">Treinamento · sem tempo</a><a class="${mode==='simulation'?'selected':''}" href="#bank/simulation">Simulação · 5 minutos</a></nav><div id="bank-content"></div>`;
  if(mode==='simulation')renderBankSimulation();else renderTraining();
}
function trainingQuestion(){
  const pool=BANK.filter(q=>q.category!=='encadeada'&&(bankFilter==='all'||q.topic===bankFilter));
  if(!pool.some(q=>q.id===state.trainingId))state.trainingId=(pool[0]||BANK[0]).id;
  return BANK.find(q=>q.id===state.trainingId);
}
function renderTraining(){
  const q=trainingQuestion(),r=state.training[q.id]||{};
  $('#bank-content').innerHTML=`<div class="bank-intro"><p><strong>Sem pressão de tempo.</strong> Responda por escrito ou em voz alta. Depois compare com o modelo e escolha o que precisa retomar.</p><label>Treinar um assunto<select id="bank-topic"><option value="all">Todos os assuntos</option>${Object.entries(C.topics).filter(([id])=>BANK.some(q=>q.topic===id)).map(([id,label])=>`<option value="${id}" ${id===bankFilter?'selected':''}>${label}</option>`).join('')}</select></label></div><section class="card bank-question"><div class="chips">${tag(q.category)}${tag(q.difficulty)}${tag(C.topics[q.topic])}</div><p class="eyebrow">PERGUNTA PARA EXPLICAR</p><h2>${esc(q.prompt)}</h2>${q.category==='codigo'?'<p>Use a área de código para procurar a resposta antes de conferir o modelo.</p><a href="#code">Abrir o firmware →</a>':''}<label for="training-answer">Sua resposta</label><textarea id="training-answer" data-training-text="${q.id}" placeholder="Como você responderia à banca?">${esc(r.text||'')}</textarea><label class="check"><input type="checkbox" data-training-spoken="${q.id}" ${r.spoken?'checked':''}> Respondi em voz alta</label><div class="button-row"><button id="training-reveal">Comparar minha resposta</button><button id="training-next" class="secondary">Sortear outra pergunta →</button></div><div id="training-feedback" aria-live="polite">${r.reviewed?bankModel(q,r,'training'):''}</div></section><p class="fine">${BANK.length} perguntas no banco, incluindo perguntas encadeadas usadas na simulação. O curso registra prática e autoavaliação, sem dar nota semântica ao texto.</p>`;
}
function bankModel(q,r,context){return `<div class="result model"><strong>Resposta-modelo</strong><p>${esc(q.model)}</p><strong>Confira os conceitos</strong><div class="chips">${q.concepts.map(tag).join('')}</div><button class="code-link" data-code="${q.ref}">Localizar no código: ${esc(q.ref)} →</button><fieldset class="self-rating"><legend>Sua autoavaliação desta resposta</legend>${[['rever','Preciso rever'],['apoio','Expliquei com apoio'],['seguro','Expliquei com segurança']].map(([v,label])=>`<label class="option"><input type="radio" name="rating-${q.id}-${context}" value="${v}" data-rating="${q.id}" data-context="${context}" ${r.rating===v?'checked':''}>${label}</label>`).join('')}</fieldset><small>Esta percepção é sua. Não há correção automática de fala ou texto.</small></div>`;}
function renderBankSimulation(){
  const s=state.session;
  if(!s){$('#bank-content').innerHTML=`<section class="card simulation-intro"><div class="timer-preview">05:00</div><h2>Uma rodada para ganhar confiança</h2><p>Seis perguntas: conceitos, hardware, programação, localização no código e uma situação com pergunta complementar. O sorteio mistura dificuldades e evita repetir as perguntas da rodada anterior quando há alternativas.</p><ul><li>O relógio continua ao navegar, fechar ou recarregar a página.</li><li>Responda por escrito ou marque que respondeu em voz alta.</li><li>Os modelos aparecem no fim; não há nota automática para respostas abertas.</li><li>Você pode encerrar antes do tempo ou deixar o cronômetro terminar.</li></ul><button id="start-bank">Iniciar simulação de 5 minutos</button></section>`;return;}
  if(s.done){renderBankReview();return;}
  const q=BANK.find(q=>q.id===s.ids[s.index]),r=s.responses[q.id]||{};
  $('#bank-content').innerHTML=`<section class="card bank-question"><div class="bank-status"><span>Pergunta ${s.index+1} de ${s.ids.length}</span><strong id="bank-timer" class="timer" role="timer" aria-label="Tempo restante">${timerText(K.remainingSeconds(s))}</strong></div><div class="chips">${tag(q.category)}${tag(q.difficulty)}</div>${q.parent?`<p class="chain-note">Pergunta complementar à situação anterior: ${esc(BANK.find(x=>x.id===q.parent).prompt)}</p>`:''}<h2>${esc(q.prompt)}</h2>${q.category==='codigo'?'<p><a href="#code">Consultar o código durante a resposta →</a> O cronômetro continua.</p>':''}<label for="session-answer">Sua resposta</label><textarea id="session-answer" data-session-text="${q.id}" placeholder="Registre as ideias principais…">${esc(r.text||'')}</textarea><label class="check"><input type="checkbox" data-session-spoken="${q.id}" ${r.spoken?'checked':''}> Respondi em voz alta</label><div class="button-row"><button id="bank-prev" class="secondary" ${s.index===0?'disabled':''}>← Anterior</button><button id="bank-next" ${s.index===s.ids.length-1?'disabled':''}>Próxima pergunta →</button><button id="finish-bank" class="text-button">Encerrar e revisar</button></div><p class="fine">Você pode voltar a perguntas anteriores. Respostas não preenchidas aparecerão como não respondidas.</p></section>`;
}
function endSession(reason='manual'){
  if(!state.session||state.session.done)return;
  state.session.done=true;state.session.ended=Math.min(Date.now(),state.session.deadline);state.session.reason=reason;
  state.previousBank=[...state.session.ids];
  state.bankHistory.push({ids:[...state.session.ids],started:state.session.started,ended:state.session.ended,answered:state.session.ids.filter(id=>hasAnswer(state.session.responses[id])).length});state.bankHistory=state.bankHistory.slice(-30);save();
  if(location.hash.startsWith('#bank/simulation'))renderBankReview();
}
function hasAnswer(r){return !!(r&&(typeof r.text==='string'&&r.text.trim()||r.spoken));}
function renderBankReview(){
  const s=state.session;if(!s)return;const count=s.ids.filter(id=>hasAnswer(s.responses[id])).length;
  $('#bank-content').innerHTML=`<div class="result success"><strong>${s.reason==='timeout'?'Os cinco minutos terminaram.':'Rodada encerrada.'}</strong><p>${count} de ${s.ids.length} perguntas respondidas. Tempo: ${timerText(Math.max(0,Math.min(300,Math.floor((s.ended-s.started)/1000))))}. Compare conteúdo e clareza; esta contagem não é uma nota de qualidade.</p></div><div class="button-row"><button id="new-bank">Preparar outra rodada</button><a class="button secondary" href="#progress">Ver minha preparação</a></div>${s.ids.map((id,i)=>{const q=BANK.find(q=>q.id===id),r=s.responses[id]||{};return `<section class="card bank-review"><p class="eyebrow">PERGUNTA ${i+1} · ${esc(q.category)}</p><h2>${esc(q.prompt)}</h2><strong>Sua resposta</strong><p class="written-answer">${esc(r.text|| (r.spoken?'Resposta feita em voz alta.':'Não respondida nesta rodada.'))}</p>${bankModel(q,r,'session')}</section>`;}).join('')}`;
}
function tick(){
  if(state.session&&!state.session.done&&K.remainingSeconds(state.session)===0)endSession('timeout');
  const active=state.session&&!state.session.done;
  $('#session-strip').hidden=!active;
  if(active){const time=timerText(K.remainingSeconds(state.session));$('#session-strip').innerHTML=`<span>Simulação de banca em andamento <strong role="timer">${time}</strong></span><a href="#bank/simulation">Voltar às perguntas →</a>`;if($('#bank-timer'))$('#bank-timer').textContent=time;}
}
function renderProgress(){
  const stats=K.topicStats(C.modules,state.answers),all=Object.values(stats),answered=all.reduce((n,s)=>n+s.answered,0),correct=all.reduce((n,s)=>n+s.correct,0),total=all.reduce((n,s)=>n+s.total,0),done=C.modules.filter(m=>K.moduleDone(m,state)).length;
  const practiced=Object.values(state.training).filter(r=>r.reviewed).length,reflections=Object.values(state.reflections).filter(r=>r.reviewed).length;
  const ratings=[...Object.values(state.training),...Object.values(state.session?.responses||{})].filter(r=>r.rating);
  const weak=Object.entries(stats).filter(([,s])=>s.answered&&s.correct<s.answered).map(([id])=>id);
  const suggested=C.modules.filter(m=>m.activities.some(q=>weak.includes(q.topic)&&q.type!=='reflect'&&state.answers[q.id]&&!K.grade(q,state.answers[q.id].value)));
  $('#main').innerHTML=`${lead('SEU APRENDIZADO','Meu progresso','Veja o que já consegue resolver e escolha o que vale retomar antes da apresentação.')}<div class="summary-grid"><div class="card"><strong>${done}/${C.modules.length}</strong><span>Módulos concluídos</span></div><div class="card"><strong>${correct}/${total}</strong><span>Atividades corretas agora</span></div><div class="card"><strong>${answered}</strong><span>Atividades objetivas respondidas</span></div><div class="card"><strong>${practiced}</strong><span>Perguntas treinadas com modelo</span></div></div><section class="card"><h2>Desempenho por assunto</h2><p>“Acertos atuais” considera sua última resposta em cada atividade. A primeira tentativa fica separada. Questões não respondidas não são tratadas como erros.</p><div class="table-scroll"><table><thead><tr><th>Assunto</th><th>Respondidas</th><th>Acertos atuais</th><th>Acertos na primeira</th><th>Cobertura</th></tr></thead><tbody>${Object.entries(C.topics).map(([id,label])=>{const s=stats[id];return s?`<tr><th scope="row">${esc(label)}</th><td>${s.answered}/${s.total}</td><td>${s.answered?s.correct+'/'+s.answered:'Ainda sem respostas'}</td><td>${s.answered?s.first+'/'+s.answered:'—'}</td><td><progress max="${s.total}" value="${s.answered}" aria-label="Cobertura de ${esc(label)}"></progress></td></tr>`:'';}).join('')}</tbody></table></div></section><section class="card"><h2>O que retomar agora</h2>${suggested.length?`<p>Há respostas recentes para revisar nestes módulos:</p><div class="chips">${suggested.map(m=>`<a class="button secondary" href="#lesson/${m.id}/practice">${esc(m.title)}</a>`).join('')}</div>`:`<p>${answered===total?'Todas as atividades objetivas estão corretas. Use a banca para treinar a explicação com suas palavras.':'Continue a trilha para reunir mais evidências de aprendizagem. Os assuntos sem resposta ainda não foram avaliados.'}</p><a href="#lesson/${(C.modules.find(m=>!K.moduleDone(m,state))||C.modules[0]).id}">Continuar a trilha →</a>`}</section><section class="card"><h2>Preparação oral · prática e autoavaliação</h2><p>${reflections} respostas de módulos comparadas com modelos · ${state.bankHistory.length} simulação(ões) encerrada(s).</p><div class="chips">${[['rever','Preciso rever'],['apoio','Com apoio'],['seguro','Com segurança']].map(([v,label])=>tag(`${label}: ${ratings.filter(r=>r.rating===v).length}`)).join('')}</div><p class="fine">Estas categorias são declarações do estudante sobre o treinamento e a última simulação. Não medem automaticamente a qualidade da fala. A tabela objetiva de “Preparação para banca” contém apenas questões fechadas.</p><a href="#bank">Praticar banca →</a></section><section class="card"><h2>Leve uma cópia do seu progresso</h2><p>O progresso fica neste navegador e neste endereço. Use o mesmo endereço ao voltar. Limpar os dados do navegador pode apagá-lo; exporte para transferir a outro computador.</p><div class="button-row"><button id="export-progress">Exportar progresso</button><label class="button secondary file-label">Importar cópia<input id="import-progress" type="file" accept="application/json,.json"></label><button data-print class="secondary">Imprimir resumo</button></div><div id="import-feedback" role="status"></div><details class="reset-area"><summary>Recomeçar o curso neste navegador</summary><p>Esta ação apaga as respostas e a preparação salvas pelo curso neste navegador. Exporte uma cópia antes se quiser guardar o histórico.</p><label class="check"><input id="reset-confirm" type="checkbox"> Quero apagar meu progresso e recomeçar</label><button id="reset-progress" class="danger">Apagar progresso</button></details></section>`;
}
function downloadProgress(){const blob=new Blob([JSON.stringify(state,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='meu-progresso-colmeia.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
document.addEventListener('submit',event=>{
  const form=event.target;
  if(form.id==='sim-form'){event.preventDefault();startSim();return;}
  if(!form.dataset.question)return;
  event.preventDefault();const q=findQ(form.dataset.question),value=readAnswer(form,q);
  if(value===null||(['fill','edit'].includes(q.type)&&!String(value).trim())||(q.type==='match'&&value.some(v=>!v))){$('#feedback-'+q.id).textContent='Preencha sua resposta antes de conferir.';return;}
  state.answers=K.record(state.answers,q,value);state.drafts[q.id]=value;save();$('#feedback-'+q.id).innerHTML=questionFeedback(q,K.grade(q,value));nav(location.hash.slice(1).split('/')[0]);
});
document.addEventListener('input',event=>{
  const e=event.target;
  if(e.dataset.reflectText){const r=state.reflections[e.dataset.reflectText] ||= {};r.text=e.value;save();}
  if(e.dataset.trainingText){const r=state.training[e.dataset.trainingText] ||= {};r.text=e.value;save();}
  if(e.dataset.sessionText&&state.session&&!state.session.done){const r=state.session.responses[e.dataset.sessionText] ||= {};r.text=e.value;save();}
  if(e.dataset.outline){state.outline[e.dataset.outline]=e.value;save();}
  const form=e.closest('form[data-question]');if(form){const q=findQ(form.dataset.question);state.drafts[q.id]=readAnswer(form,q);save();if(state.answers[q.id])$('#feedback-'+q.id).textContent='Resposta alterada. Confira novamente para atualizar o resultado.';}
  if(e.id==='code-search')searchCode();
  if(e.id==='sim-interval')$('#interval-output').textContent=e.value+' minuto(s)';
  if(e.id.startsWith('condition-')||e.id==='battery-value'||e.id.startsWith('audio-'))updateLabs();
});
document.addEventListener('change',async event=>{
  const e=event.target;
  if(e.dataset.reflectSpoken){(state.reflections[e.dataset.reflectSpoken] ||= {}).spoken=e.checked;save();}
  if(e.dataset.trainingSpoken){(state.training[e.dataset.trainingSpoken] ||= {}).spoken=e.checked;save();}
  if(e.dataset.sessionSpoken&&state.session&&!state.session.done){(state.session.responses[e.dataset.sessionSpoken] ||= {}).spoken=e.checked;save();}
  if(e.dataset.rating){const collection=e.dataset.context==='session'?state.session.responses:state.training;(collection[e.dataset.rating] ||= {}).rating=e.value;save();}
  if(e.id==='function-jump'&&e.value)location.hash='code/'+e.value;
  if(e.id==='sim-preset')presetSim(e.value);
  if(e.id==='bank-topic'){bankFilter=e.value;state.trainingId=null;renderTraining();save();}
  if(e.id==='import-progress'&&e.files[0]){
    try{if(e.files[0].size>3_000_000)throw Error('size');const imported=restore(JSON.parse(await e.files[0].text()));state=imported;save();showNotice('Cópia importada. O progresso neste navegador foi substituído pelo conteúdo do arquivo.');renderProgress();tick();}
    catch{$('#import-feedback').textContent='Arquivo inválido ou incompatível. Seu progresso atual foi preservado.';}
  }
});
document.addEventListener('click',event=>{
  const e=event.target.closest('button,a,input');if(!e)return;
  if(e.dataset.code){openCode(e.dataset.code);return;}
  if(e.dataset.dialogLink!==undefined){$('#code-dialog').close();return;}
  if(e.id==='close-dialog'){$('#code-dialog').close();return;}
  if(e.dataset.component){const map=e.closest('.hardware-map'),c=components[e.dataset.component];$$('[data-component]',map).forEach(b=>b.setAttribute('aria-pressed',String(b===e)));map.nextElementSibling.innerHTML=`<strong>${esc(c.name)}</strong><p>${esc(c.detail)}</p><button class="code-link" data-code="${c.ref}">Relacionar ao código →</button>`;return;}
  if(e.dataset.reflectReview){const id=e.dataset.reflectReview,q=findQ(id),r=state.reflections[id] ||= {};if(!hasAnswer(r)){$('#feedback-'+id).textContent='Escreva uma resposta ou marque que respondeu em voz alta antes de comparar.';return;}r.reviewed=true;save();$('#feedback-'+id).innerHTML=reflectionFeedback(q);nav('lesson');return;}
  if(e.dataset.order){const id=e.dataset.order,position=Number(e.dataset.position),destination=position+Number(e.dataset.direction),items=orderDrafts[id];if(destination<0||destination>=items.length)return;[items[position],items[destination]]=[items[destination],items[position]];state.drafts[id]=[...items];save();const section=$('#q-'+id);section.outerHTML=renderQuestion(findQ(id));const target=$(`[data-order="${id}"][data-position="${destination}"][data-direction="${e.dataset.direction}"]:not([disabled])`)||$(`[data-order="${id}"][data-position="${destination}"]:not([disabled])`);target?.focus();return;}
  if(e.dataset.sourceLine){selectLine(Number(e.dataset.sourceLine));return;}
  if(e.id==='search-next'||e.id==='search-prev'){if(searchMatches.length){searchIndex=(searchIndex+(e.id==='search-next'?1:-1)+searchMatches.length)%searchMatches.length;showMatch();}return;}
  if(e.id==='sim-next'||e.id==='sim-all'){if(simPlan){simStep=e.id==='sim-all'?9:Math.min(9,simStep+1);if(simStep===9)finishSim();updateSimView();}return;}
  if(e.id==='sim-prev'){simStep=Math.max(0,simStep-1);updateSimView();return;}
  if(e.dataset.simStep!==undefined&&simPlan){simStep=Number(e.dataset.simStep);updateSimView();return;}
  if(e.id==='sim-later'){
    if(simPlan&&!simCommitted){showNotice('Conclua o ciclo atual para avançar à próxima tentativa.');return;}
    state.sim.now=state.sim.next===null?state.sim.now+120:Math.max(state.sim.now,state.sim.next);state.sim.secondsSince=7200;save();renderSimulator();$('#sim-wifi').checked=true;$('#sim-firebase').checked=true;return;
  }
  if(e.id==='sim-reset'){state.sim=K.newSimulation();save();renderSimulator();return;}
  if(e.id==='training-reveal'){const q=trainingQuestion(),r=state.training[q.id] ||= {};if(!hasAnswer(r)){$('#training-feedback').textContent='Responda por escrito ou marque a resposta em voz alta antes de comparar.';return;}r.reviewed=true;save();$('#training-feedback').innerHTML=bankModel(q,r,'training');return;}
  if(e.id==='training-next'){const q=trainingQuestion(),pool=BANK.filter(x=>x.category!=='encadeada'&&x.id!==q.id&&(bankFilter==='all'||x.topic===bankFilter));if(!pool.length){showNotice('Não há outra pergunta neste filtro. Escolha outro assunto para variar o treino.');return;}state.trainingId=K.shuffle(pool)[0].id;save();renderTraining();return;}
  if(e.id==='start-bank'){const started=Date.now();state.session={ids:K.selectBank(BANK,state.previousBank),started,deadline:started+300000,index:0,responses:{},done:false};save();renderBankSimulation();tick();return;}
  if(e.id==='bank-prev'||e.id==='bank-next'){const s=state.session;if(s&&!s.done){s.index=Math.max(0,Math.min(s.ids.length-1,s.index+(e.id==='bank-next'?1:-1)));save();renderBankSimulation();}return;}
  if(e.id==='finish-bank'){endSession();tick();return;}
  if(e.id==='new-bank'){state.session=null;save();renderBankSimulation();return;}
  if(e.id==='export-progress'){downloadProgress();return;}
  if(e.id==='reset-progress'){if(!$('#reset-confirm').checked){showNotice('Marque a confirmação para apagar seu progresso.');return;}state=defaults();orderDrafts={};save();showNotice('Progresso apagado. Você pode começar novamente.');renderProgress();nav('progress');tick();return;}
  if(e.dataset.print!==undefined){window.print();return;}
  if(e.id==='menu-toggle'){const open=document.body.classList.toggle('menu-open');e.setAttribute('aria-expanded',String(open));e.textContent=open?'Fechar menu':'Abrir menu';}
});
$('#code-dialog').addEventListener('click',e=>{if(e.target===$('#code-dialog'))$('#code-dialog').close();});
window.addEventListener('hashchange',route);
window.addEventListener('pagehide',save);
window.addEventListener('visibilitychange',tick);
setInterval(tick,1000);
if(storageProblem)showNotice(storageProblem);
if(!location.hash&&state.route!=='home')location.hash=state.route;
else route();
})();
