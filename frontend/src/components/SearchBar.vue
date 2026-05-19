<template>
  <div class="searchbar" :class="{ 'is-focused': focused, 'has-value': localQuery.length > 0 }">
    <svg class="searchbar-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true">
      <circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" stroke-width="1.6" />
      <line x1="16.5" y1="16.5" x2="21" y2="21" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
    </svg>
    <input
      v-model="localQuery"
      type="text"
      role="combobox"
      :aria-label="searchAriaLabel"
      aria-controls="search-results-list"
      :aria-expanded="results.length > 0"
      placeholder="Search data items, e.g. 'aged care staff numbers'"
      @input="onInput"
      @focus="focused = true"
      @blur="focused = false"
      @keydown.escape="onClear"
    />
    <button
      v-if="localQuery"
      type="button"
      class="searchbar-clear"
      aria-label="Clear search"
      @click="onClear"
    >
      <svg viewBox="0 0 24 24" width="14" height="14" aria-hidden="true">
        <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
        <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
      </svg>
    </button>
    <kbd v-else class="searchbar-kbd" aria-hidden="true">Esc</kbd>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue';
import { useStore } from 'vuex';

const store = useStore();
const searchAriaLabel = computed(() => store.state.corpus.ui.searchAriaLabel ?? 'Search');
const results = computed(() => store.state.search.results);
const localQuery = ref('');
const focused = ref(false);

watch(() => store.state.search.query, (val) => {
  if (val !== localQuery.value) localQuery.value = val;
});
let debounceTimer = null;

onUnmounted(() => { clearTimeout(debounceTimer); });

function onInput() {
  clearTimeout(debounceTimer);
  if (!localQuery.value) { store.dispatch('search/clear'); return; }
  debounceTimer = setTimeout(() => store.dispatch('search/query', localQuery.value), 300);
}

function onClear() {
  localQuery.value = '';
  store.dispatch('search/clear');
}
</script>

<style scoped>
.searchbar {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 0.1rem 0.6rem 0.1rem 0.85rem;
  box-shadow: 0 1px 0 rgba(10, 10, 10, 0.02);
  transition: border-color 0.25s var(--ease), box-shadow 0.25s var(--ease), background 0.25s var(--ease);
}

.searchbar.is-focused {
  border-color: color-mix(in srgb, var(--accent) 55%, var(--line));
  box-shadow:
    0 0 0 4px var(--accent-ring),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

.searchbar-icon {
  color: var(--muted-2);
  flex-shrink: 0;
  transition: color 0.25s var(--ease);
}

.searchbar.is-focused .searchbar-icon { color: var(--accent); }

.searchbar input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font: inherit;
  font-size: 1rem;
  padding: 0.85rem 0;
  color: var(--ink);
  letter-spacing: -0.005em;
}

.searchbar input::placeholder {
  color: var(--muted-2);
  font-weight: 400;
}

.searchbar-clear {
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--muted-2);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.35rem;
  border-radius: 8px;
  transition: background 0.2s var(--ease), color 0.2s var(--ease);
}

.searchbar-clear:hover { background: var(--line-soft); color: var(--ink); }

.searchbar-kbd {
  font-family: var(--font-mono);
  font-size: 0.65rem;
  color: var(--muted-2);
  background: var(--line-soft);
  border: 1px solid var(--line);
  border-radius: 5px;
  padding: 0.1rem 0.4rem;
  letter-spacing: 0.04em;
}
</style>
