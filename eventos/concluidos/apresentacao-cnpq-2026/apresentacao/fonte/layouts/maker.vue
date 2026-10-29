<script setup lang="ts">
defineProps<{ number?: number, section?: string }>()
</script>

<template>
  <div class="slidev-layout maker">
    <div class="slide-content"><slot /></div>
    <footer class="deck-footer">
      <span>IFG <b>·</b> Câmpus Águas Lindas</span>
      <span>{{ section || 'Laboratório Maker' }}</span>
      <span>{{ String(number || 1).padStart(2, '0') }} <b>/</b> 25</span>
    </footer>
  </div>
</template>
