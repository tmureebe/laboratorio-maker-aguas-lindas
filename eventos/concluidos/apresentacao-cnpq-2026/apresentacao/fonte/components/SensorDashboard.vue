<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
const props = defineProps<{ dataset: 'estacao' | 'colmeia' }>()
type Reading = { data: string; tempo: string; [key: string]: string | number | boolean | null }
const payload = ref<{total:number,inicio:string,fim:string,registros:Reading[]}>()
const selected = ref('temperatura'), period = ref('todos'), cursor = ref<number | null>(null), error = ref(false)
const metrics = computed(() => props.dataset === 'estacao'
  ? [{ key: 'temperatura', label: 'Temperatura', unit: '°C' }, { key: 'umidade', label: 'Umidade', unit: '%' }, { key: 'pressao', label: 'Pressão', unit: 'hPa' }]
  : [{ key: 'temperatura', label: 'Temperatura interna', unit: '°C' }, { key: 'umidade', label: 'Umidade interna', unit: '%' }, { key: 'audio', label: 'Nível de áudio', unit: 'dBFS' }])
const metric = computed(() => metrics.value.find(m => m.key === selected.value)!)
const rows = computed(() => {
  const all = payload.value?.registros || []
  if (period.value === 'todos' || !all.length) return all
  const lastDay = all[all.length - 1].data.slice(0,10)
  return all.filter(r => r.data.startsWith(lastDay))
})
const last = computed(() => rows.value.at(-1))
const shown = computed(() => cursor.value === null ? last.value : rows.value[cursor.value])
const fmt = (n: unknown, digits = 1) => typeof n === 'number' ? n.toLocaleString('pt-BR', { maximumFractionDigits: digits, minimumFractionDigits: digits }) : '—'
const extent = computed(() => {
  const vals = rows.value.map(r => r[selected.value]).filter((v): v is number => typeof v === 'number' && Number.isFinite(v))
  if (!vals.length) return [0, 1]
  const lo = Math.min(...vals), hi = Math.max(...vals), pad = Math.max((hi-lo)*.12, .5)
  return [lo-pad,hi+pad]
})
const tx = (r: Reading) => {
  const start=Date.parse(rows.value[0].tempo),end=Date.parse(rows.value.at(-1)!.tempo)
  return 68 + (Date.parse(r.tempo)-start)/(end-start || 1)*982
}
const ty = (value: number) => 218 - (value-extent.value[0])/(extent.value[1]-extent.value[0])*188
const path = computed(() => {
  let previous = 0
  return rows.value.map(r => {
    const value = r[selected.value], time = Date.parse(r.tempo)
    if (typeof value !== 'number') { previous = 0; return '' }
    // Intervalos sem coleta não são interpolados: uma nova linha começa após 45 minutos.
    const command = !previous || time-previous>45*60*1000 ? 'M' : 'L'; previous = time
    return `${command}${tx(r).toFixed(2)},${ty(value).toFixed(2)}`
  }).join(' ')
})
const comparison = computed(() => {
  if (props.dataset !== 'colmeia' || !['temperatura','umidade'].includes(selected.value)) return ''
  const field=selected.value === 'temperatura' ? 'externa' : 'umidadeExterna'
  return rows.value.map(r => typeof r[field]==='number' ? `${tx(r).toFixed(2)},${ty(r[field] as number).toFixed(2)}` : '').filter(Boolean).join(' ')
})
function inspect(e: MouseEvent) {
  const box = e.currentTarget instanceof Element ? e.currentTarget.getBoundingClientRect() : null
  if (!box || !rows.value.length) return
  const fraction = Math.max(0,Math.min(1,((e.clientX-box.left)/box.width*1100-68)/982))
  const start=Date.parse(rows.value[0].tempo),end=Date.parse(rows.value.at(-1)!.tempo), wanted=start+fraction*(end-start)
  let best=0; rows.value.forEach((r,i)=>{if(Math.abs(Date.parse(r.tempo)-wanted)<Math.abs(Date.parse(rows.value[best].tempo)-wanted))best=i})
  cursor.value=best
}
onMounted(async () => {
  try { const result = await fetch(`/dados/${props.dataset}.json`); if(!result.ok) throw new Error('Arquivo local indisponível'); payload.value=await result.json() }
  catch { error.value=true }
})
</script>

<template>
  <section class="sensor-dashboard" @pointerdown.stop @keydown.stop>
    <div class="data-toolbar">
      <span class="status-pill">ARQUIVO LOCAL · DADOS REGISTRADOS</span>
      <label>Período <select v-model="period" @change="cursor=null"><option value="todos">Todo o arquivo</option><option value="ultimo">Último dia registrado</option></select></label>
    </div>
    <p v-if="error" class="data-error">Não foi possível abrir os dados locais. Use o PDF de apoio.</p>
    <template v-if="payload">
      <div class="data-metrics">
        <button v-for="m in metrics" :key="m.key" :class="{ active: selected===m.key }" @click="selected=m.key; cursor=null" :aria-pressed="selected===m.key">
          <span>{{ m.label }}</span><strong>{{ fmt(shown?.[m.key]) }} <small>{{ m.unit }}</small></strong>
        </button>
        <div v-if="dataset==='colmeia'" class="lid-state"><span>Tampa</span><strong>{{ shown?.tampa ? 'Aberta' : 'Fechada' }}</strong><small>Estado registrado</small></div>
      </div>
      <svg class="sensor-chart" viewBox="0 0 1100 267" role="img" :aria-label="`Histórico de ${metric.label}, ${payload.inicio} a ${payload.fim}`" @mousemove="inspect" @mouseleave="cursor=null">
        <g v-for="i in [0,1,2,3]" :key="i">
          <line x1="68" :y1="30+i*188/3" x2="1050" :y2="30+i*188/3" stroke="#dbe4dc" />
          <text x="55" :y="36+i*188/3" text-anchor="end">{{ fmt(extent[1]-i*(extent[1]-extent[0])/3) }}</text>
        </g>
        <path :d="path" fill="none" stroke="#186447" stroke-width="3" />
        <circle v-for="(r,i) in rows" :key="i" v-show="typeof r[selected]==='number'" :cx="tx(r)" :cy="ty(Number(r[selected]))" r="2.2" fill="#186447" />
        <text x="68" y="250">{{ rows[0]?.data.slice(0,10) }}</text><text x="1050" y="250" text-anchor="end">{{ last?.data.slice(0,10) }}</text>
        <g v-if="shown && typeof shown[selected]==='number'">
          <line :x1="tx(shown)" y1="24" :x2="tx(shown)" y2="218" stroke="#b54e2c" stroke-dasharray="5 5" />
          <circle :cx="tx(shown)" :cy="ty(Number(shown[selected]))" r="6" fill="#b54e2c" stroke="white" stroke-width="2" />
        </g>
      </svg>
      <div class="data-caption"><span>{{ cursor===null ? 'Última medição' : 'Medição selecionada' }}: <b>{{ shown?.data }}</b> · UTC−03:00</span><span>{{ rows.length.toLocaleString('pt-BR') }} registros no recorte</span></div>
    </template>
  </section>
</template>
