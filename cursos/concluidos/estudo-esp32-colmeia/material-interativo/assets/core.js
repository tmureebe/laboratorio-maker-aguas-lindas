/* Pure logic shared by the browser and the automated tests. No network or eval. */
(function(root){
'use strict';
const normalize=v=>String(v ?? '').trim().replace(/\s+/g,' ');
function grade(q,value){
  if(q.type==='reflect') return null;
  if(['choice','tf','predict','line','locate'].includes(q.type)) return String(value)===String(q.answer);
  if(['fill','edit'].includes(q.type)) return q.answers.some(a=>normalize(a)===normalize(value));
  if(q.type==='match') return Array.isArray(value)&&value.length===q.pairs.length&&q.pairs.every((p,i)=>value[i]===p[1]);
  if(q.type==='order') return Array.isArray(value)&&value.length===q.items.length&&value.every((v,i)=>Number(v)===i);
  return false;
}
function record(answers,q,value){
  const correct=grade(q,value), old=answers[q.id];
  return {...answers,[q.id]:{value,correct,attempts:(old?.attempts||0)+1,firstCorrect:old?old.firstCorrect:correct}};
}
function topicStats(modules,answers){
  const stats={};
  for(const m of modules) for(const q of m.activities){
    if(q.type==='reflect') continue;
    const s=stats[q.topic] ||= {total:0,answered:0,correct:0,first:0};s.total++;
    if(answers[q.id]){s.answered++;if(grade(q,answers[q.id].value))s.correct++;if(answers[q.id].firstCorrect)s.first++;}
  }
  return stats;
}
function moduleDone(m,state){return m.activities.every(q=>q.type==='reflect'?state.reflections[q.id]?.reviewed:grade(q,state.answers[q.id]?.value)===true);}
function shuffle(items,rng=Math.random){const out=[...items];for(let i=out.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[out[i],out[j]]=[out[j],out[i]];}return out;}
function selectBank(bank,previous=[],rng=Math.random){
  const picked=[];
  for(const category of ['conceito','hardware','programacao','codigo','cenario']){
    let candidates=bank.filter(q=>q.category===category&&!previous.includes(q.id));
    if(!candidates.length)candidates=bank.filter(q=>q.category===category);
    // The first question is approachable, and the code question challenges interpretation.
    const preferred=category==='conceito'?candidates.filter(q=>q.difficulty==='básica'):category==='codigo'?candidates.filter(q=>q.difficulty!=='básica'):candidates;
    picked.push(shuffle(preferred.length?preferred:candidates,rng)[0]);
  }
  const chain=bank.find(q=>q.id===picked[4].followup);
  if(chain)picked.push(chain);
  return picked.map(q=>q.id);
}
const remainingSeconds=(session,now=Date.now())=>Math.max(0,Math.ceil((session.deadline-now)/1000));
const windowOpen=minute=>{const hour=Math.floor(((minute%1440)+1440)%1440/60);return hour>=6&&hour<=22;};
function nextSlot(minute){const day=Math.floor(minute/1440)*1440;const h=Math.floor((minute-day)/60);if(h<6)return day+360;if(h>=22)return day+1800;return day+(6+(Math.floor((h-6)/2)+1)*2)*60;}
function newSimulation(){return {now:480,queue:0,history:0,events:0,lost:0,boot:0,next:480,secondsSince:0,lastSleep:0,clock:true};}
function simulateCycle(previous,options={}){
  const s={...previous};
  const o={wifi:true,storage:true,sensor:true,firebase:true,ntp:true,lid:false,cause:'timer',interval:600,clock:s.clock,...options};
  o.interval=Math.max(60,Math.min(3600,Number(o.interval)||600));
  if(Number.isFinite(o.now))s.now=o.now;
  s.clock=!!o.clock;
  if(o.cause==='power'){s.next=null;s.secondsSince=0;s.lastSleep=0;s.boot=0;}
  if(o.cause==='timer')s.secondsSince=Math.min(604800,s.secondsSince+s.lastSleep);
  s.boot++;
  const steps=[];const add=(label,detail,ref)=>steps.push({label,detail,ref,snapshot:{...s}});
  add('Acorda',`Ciclo ${s.boot}: início de setup().`,'setup');
  add('Identifica o motivo',({timer:'Despertar pelo temporizador.',lid:'Despertar pela tampa (EXT0).',power:'Inicialização ou reset.'})[o.cause],'wakeupCauseText');
  add('Inicializa',o.storage?'LittleFS e sensores preparados. A fila anterior continua disponível.':'Falha local simulada: não será possível gravar a ficha atual.','initializeLocalStorage');
  add('Lê sensores',`Tampa ${o.lid?'aberta (HIGH)':'fechada (LOW)'}. ${o.sensor?'DHT11 externo: 25 °C e 60% (valores fictícios).':'DHT11 externo falhou: temperatura e umidade ficam inválidas.'}`,'readDHTSensors');
  add('Processa dados','Reconstrói tensão, estima percentual e resume o áudio. O fim das leituras é marcado para calcular a hora da medição.','readAudioFeatures');
  const periodicCheck=s.clock?(windowOpen(s.now)&&(s.next===null||s.now>=s.next)):(o.cause==='power'||s.secondsSince>=7200);
  let open=s.clock&&windowOpen(s.now);
  let periodic=periodicCheck&&open;
  let lidAllowed=o.cause==='lid'&&open;
  const wifiNeeded=periodicCheck||lidAllowed||(o.cause==='lid'&&!s.clock);
  const connected=wifiNeeded&&o.wifi;
  let connectText=wifiNeeded?(connected?'Wi-Fi conectado.':'Tentativa de Wi-Fi falhou; a conexão tem limite de espera.'):'Wi-Fi permanece desligado nesta coleta.';
  if(connected){
    if(!s.clock&&o.ntp)s.clock=true;
    if(s.clock){open=windowOpen(s.now);periodic=open&&(s.next===null||s.now>=s.next);lidAllowed=o.cause==='lid'&&open;
      connectText+=open?' Relógio válido: janela diurna aberta.':' Relógio válido: fora da janela; Firebase bloqueado.';
      if(!open&&(s.next===null||s.now>=s.next)){s.next=nextSlot(s.now);s.secondsSince=0;}
    }else{periodic=false;lidAllowed=false;connectText+=' Sem hora válida após NTP: Firebase bloqueado.';}
  }
  add('Decide Wi-Fi e horário',connectText,'periodicUploadIsDue');
  const reading={temperature:o.sensor?25:null,humidity:o.sensor?60:null,lid:o.lid,cause:o.cause,timeValid:s.clock};
  let storeText='Grava a ficha antes das tentativas de envio ao Firebase.';
  if(o.storage){if(s.queue>=2016){s.queue--;s.lost++;storeText='Fila cheia: remove a mais antiga e grava a atual.';}s.queue++;}
  else{storeText='Não conseguiu preservar a medição atual na flash.';}
  add('Armazena',storeText,'appendStoredReading');
  let sent=0,event=false,batches=0;const messages=[];
  if(connected&&lidAllowed){if(o.firebase){s.events++;event=true;messages.push('Evento da tampa enviado.');}else messages.push('Evento falhou; não será recriado como POST pelo envio futuro do histórico.');}
  if(connected&&periodic){
    if(o.firebase){sent=o.storage?s.queue:1;batches=Math.ceil(sent/12);s.history+=sent;if(o.storage)s.queue=0;messages.push(o.storage?`Histórico confirmou ${sent} medição(ões), em ${batches} lote(s) de até 12. Fila esvaziada.`:'Medição atual enviada diretamente, pois a gravação local falhou.');}
    else messages.push('Firebase falhou; as fichas armazenadas permanecem na fila.');
  }
  if(!o.storage&&!(connected&&periodic&&o.firebase)){s.lost++;messages.push('Medição atual perdida: não foi gravada nem entregue ao histórico.');}
  if(!messages.length)messages.push('Sem envio de histórico ou evento neste ciclo. Dados gravados aguardam a próxima tentativa permitida.');
  add('Envia se permitido',messages.join(' '),'uploadQueuedReadings');
  if(periodic){s.next=s.clock?nextSlot(s.now):null;s.secondsSince=0;}
  else if(periodicCheck&&!s.clock){s.next=null;s.secondsSince=0;}
  add('Atualiza a agenda',periodic?'Tentativa periódica contabilizada, mesmo se houve falha.':'A agenda é mantida ou ajustada conforme a consulta de horário.','markPeriodicUploadAttempt');
  s.lastSleep=o.lid?60:o.interval;
  add('Entra em deep sleep',`Desliga I2S e rádio. Dorme ${s.lastSleep} s. ${o.lid?'EXT0 não habilitado neste sono; tampa já aberta.':'Temporizador e despertar por tampa habilitados.'}`,'goToSleep');
  // A fixed illustrative active time makes the distinction from exact periodic sampling visible.
  s.now+=s.lastSleep/60+10/60;
  return {steps,state:s,reading,sent,event,batches,wifiNeeded,connected,periodic,activeSeconds:10};
}
root.CourseCore={normalize,grade,record,topicStats,moduleDone,shuffle,selectBank,remainingSeconds,windowOpen,nextSlot,newSimulation,simulateCycle};
})(typeof window==='undefined'?globalThis:window);
