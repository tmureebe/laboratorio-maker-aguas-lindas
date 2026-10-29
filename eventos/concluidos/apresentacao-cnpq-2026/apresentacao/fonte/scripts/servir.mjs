import http from 'node:http'
import { createReadStream, statSync, existsSync } from 'node:fs'
import { resolve, extname, sep } from 'node:path'
import { pathToFileURL } from 'node:url'

const mime = {'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json','.jpg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml','.mp4':'video/mp4','.glb':'model/gltf-binary','.ttf':'font/ttf','.woff':'font/woff','.woff2':'font/woff2','.pdf':'application/pdf'}
export async function serve(directory, port=4173) {
  const root = resolve(directory)
  const server=http.createServer((req,res)=>{
    let pathname
    try { pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname) } catch {res.writeHead(400);res.end();return}
    let file=resolve(root,'.'+pathname)
    if(file!==root && !file.startsWith(root+sep)){res.writeHead(403);res.end();return}
    if(existsSync(file)&&statSync(file).isDirectory())file=resolve(file,'index.html')
    if(!existsSync(file)&&!extname(file))file=resolve(root,'index.html')
    if(!existsSync(file)){res.writeHead(404);res.end('Arquivo não encontrado');return}
    const stat=statSync(file),headers={'Content-Type':mime[extname(file)]||'application/octet-stream','Accept-Ranges':'bytes','Cache-Control':'no-cache'}
    const range=req.headers.range?.match(/^bytes=(\d+)-(\d*)$/)
    if(range){
      const start=Number(range[1]),end=Math.min(range[2]?Number(range[2]):stat.size-1,stat.size-1)
      if(start>end){res.writeHead(416,{'Content-Range':`bytes */${stat.size}`});res.end();return}
      res.writeHead(206,{...headers,'Content-Length':end-start+1,'Content-Range':`bytes ${start}-${end}/${stat.size}`})
      if(req.method==='HEAD')res.end();else createReadStream(file,{start,end}).pipe(res)
    }else{
      res.writeHead(200,{...headers,'Content-Length':stat.size})
      if(req.method==='HEAD')res.end();else createReadStream(file).pipe(res)
    }
  })
  await new Promise((ready,reject)=>{server.once('error',reject);server.listen(port,'127.0.0.1',ready)})
  return {server,url:`http://127.0.0.1:${server.address().port}`}
}
if(process.argv[1] && import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
  const {url}=await serve(process.argv[2]||'../04-exportacoes/web',Number(process.argv[3]||4173))
  console.log(`Apresentação local: ${url}\nMantenha esta janela aberta. Ctrl+C encerra.`)
}
