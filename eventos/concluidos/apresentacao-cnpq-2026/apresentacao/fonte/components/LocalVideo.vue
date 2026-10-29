<script setup lang="ts">
import { ref, watch, onBeforeUnmount } from 'vue'
import { useNav } from '@slidev/client'
defineProps<{ src: string, poster: string, label: string }>()
const player = ref<HTMLVideoElement>()
const { currentPage } = useNav()
watch(currentPage, () => player.value?.pause())
onBeforeUnmount(() => player.value?.pause())
</script>

<template>
  <figure class="video-card" @pointerdown.stop @keydown.stop>
    <video ref="player" :src="src" :poster="poster" :aria-label="label" controls playsinline preload="metadata" />
    <img class="video-poster-print" :src="poster" :alt="label" />
    <figcaption>{{ label }}</figcaption>
  </figure>
</template>
