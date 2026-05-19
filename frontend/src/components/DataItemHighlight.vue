<script setup>
import { watch, onUnmounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
let highlightTimer;

function applyHighlight(itemId) {
  if (!itemId) return;

  const el = document.querySelector(`[data-item-id="${itemId}"]`);
  if (!el) return;

  const collapsible = el.closest('[data-collapsible]');
  if (collapsible) collapsible.setAttribute('open', '');

  clearTimeout(highlightTimer);
  el.classList.remove('search-highlight');
  // Force reflow so re-highlighting the same element restarts the animation
  void el.offsetHeight;

  el.scrollIntoView?.({ behavior: 'smooth', block: 'center' });
  el.classList.add('search-highlight');
  highlightTimer = setTimeout(() => el.classList.remove('search-highlight'), 3000);
}

watch(() => route.query.highlight, applyHighlight, { immediate: true });

onUnmounted(() => {
  clearTimeout(highlightTimer);
});
</script>

<template><div><slot /></div></template>
