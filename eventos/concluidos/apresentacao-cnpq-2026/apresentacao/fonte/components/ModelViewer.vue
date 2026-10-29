<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/addons/controls/OrbitControls.js'
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js'

const models = [
  { id: 'colmeia-caixa', label: 'Colmeia · caixa e encaixes', description: 'Caixa, tampa deslizante e molduras para o projeto da colmeia.' },
  { id: 'estacao-caixa', label: 'Estação · caixa de proteção', description: 'Invólucro com abertura lateral e beiral, modelado para a estação.' },
  { id: 'calorimetro', label: 'Calorímetro · corpo', description: 'Corpo cilíndrico com furos, dreno e passagem para os fios.' },
  { id: 'piramides-prisma', label: 'Matemática · três pirâmides', description: 'Três peças com pinos e encaixes que recompõem um prisma triangular.' },
]
const selected = ref(0), target = ref<HTMLDivElement>(), ready = ref(false), failed = ref(false)
let scene: THREE.Scene, camera: THREE.PerspectiveCamera, renderer: THREE.WebGLRenderer
let controls: OrbitControls, model: THREE.Object3D | undefined, observer: ResizeObserver
let token = 0, disposed = false

function render() { if (!disposed && renderer && scene && camera) renderer.render(scene, camera) }
function fit() {
  if (!model || !target.value) return
  const bounds = new THREE.Box3().setFromObject(model)
  const center = bounds.getCenter(new THREE.Vector3()), size = bounds.getSize(new THREE.Vector3())
  const direction = new THREE.Vector3(.9,.65,1).normalize()
  const right = new THREE.Vector3().crossVectors(camera.up,direction).normalize()
  const up = new THREE.Vector3().crossVectors(direction,right).normalize()
  const tangent = Math.tan(THREE.MathUtils.degToRad(camera.fov / 2))
  let distance = 0
  model.updateMatrixWorld(true)
  const corner = new THREE.Vector3()
  model.traverse((part) => {
    if (!(part instanceof THREE.Mesh)) return
    const positions = part.geometry.getAttribute('position')
    for (let i=0;i<positions.count;i++) {
      corner.fromBufferAttribute(positions,i).applyMatrix4(part.matrixWorld).sub(center)
      distance = Math.max(distance, corner.dot(direction)+Math.max(Math.abs(corner.dot(up))/tangent,Math.abs(corner.dot(right))/(tangent*camera.aspect)))
    }
  })
  distance *= 1.18
  camera.position.copy(center).add(direction.multiplyScalar(distance))
  camera.near = distance / 100; camera.far = distance * 100; camera.updateProjectionMatrix()
  controls.target.copy(center); controls.minDistance = distance * .35; controls.maxDistance = distance * 3.5
  controls.update(); render()
}
function freeObject(object?: THREE.Object3D) {
  object?.traverse((child) => {
    if (child instanceof THREE.Mesh) {
      child.geometry.dispose()
      ;(Array.isArray(child.material) ? child.material : [child.material]).forEach(m => m.dispose())
    }
  })
}
async function load() {
  ready.value = false; failed.value = false
  if (!renderer) { failed.value = true; return }
  const thisToken = ++token
  try {
    const result = await new GLTFLoader().loadAsync(`/modelos-3d/${models[selected.value].id}.glb`)
    if (disposed || thisToken !== token) { freeObject(result.scene); return }
    if (model) { scene.remove(model); freeObject(model) }
    model = result.scene; scene.add(model); fit(); ready.value = true
  } catch { failed.value = true }
}
function zoom(multiplier: number) {
  if (!controls || !camera) return
  const offset = camera.position.clone().sub(controls.target).multiplyScalar(multiplier)
  offset.clampLength(controls.minDistance, controls.maxDistance)
  camera.position.copy(controls.target).add(offset); controls.update(); render()
}
function rotate() {
  if (!model) return
  model.rotation.y += Math.PI / 6; fit()
}
onMounted(async () => {
  await nextTick()
  try {
    scene = new THREE.Scene(); scene.background = new THREE.Color('#e9eee9')
    camera = new THREE.PerspectiveCamera(38, 1, .001, 100)
    renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true })
    renderer.setPixelRatio(2)
    renderer.outputColorSpace = THREE.SRGBColorSpace
    renderer.toneMapping = THREE.ACESFilmicToneMapping
    renderer.toneMappingExposure = .9
    renderer.domElement.setAttribute('aria-label', 'Modelo 3D: arraste para girar e use a roda para aproximar')
    renderer.domElement.setAttribute('role', 'img')
    target.value!.appendChild(renderer.domElement)
    scene.add(new THREE.HemisphereLight(0xffffff, 0x63756a, 1.3))
    const light = new THREE.DirectionalLight(0xffffff, 2.2); light.position.set(3,4,5); scene.add(light)
    controls = new OrbitControls(camera, renderer.domElement)
    controls.enablePan = false; controls.addEventListener('change', render)
    observer = new ResizeObserver(() => {
      const width = target.value!.clientWidth, height = target.value!.clientHeight
      if (!width || !height) return
      renderer.setSize(width, height); camera.aspect = width / height; camera.updateProjectionMatrix(); if(model) fit(); else render()
    })
    observer.observe(target.value!)
    await load()
  } catch { failed.value = true }
})
onBeforeUnmount(() => {
  disposed = true; token++; observer?.disconnect(); controls?.dispose(); freeObject(model); renderer?.dispose()
})
</script>

<template>
  <div class="model-viewer" @pointerdown.stop @keydown.stop @wheel.stop>
    <div class="model-toolbar">
      <label for="model-choice">Modelo</label>
      <select id="model-choice" v-model="selected" @change="load">
        <option v-for="(item, i) in models" :key="item.id" :value="i">{{ item.label }}</option>
      </select>
      <button @click="zoom(.8)" aria-label="Aproximar modelo">+</button>
      <button @click="zoom(1.25)" aria-label="Afastar modelo">−</button>
      <button @click="rotate" aria-label="Girar modelo">Girar</button>
      <button @click="fit" aria-label="Enquadrar modelo">Enquadrar</button>
    </div>
    <div class="model-stage">
      <div ref="target" class="model-canvas" :class="{ 'is-ready': ready }" :data-ready="ready" />
      <img v-if="!ready || failed" class="model-fallback" :src="`/modelos-3d/${models[selected].id}.jpg`" :alt="models[selected].label" />
      <img class="model-print" :src="`/modelos-3d/${models[selected].id}.jpg`" :alt="models[selected].label" />
      <span class="model-hint">{{ failed ? 'Vista estática do modelo' : 'Arraste para girar · use a roda para aproximar' }}</span>
    </div>
    <p class="model-description">{{ models[selected].description }}</p>
  </div>
</template>
