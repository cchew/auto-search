<template>
  <transition name="results-pop">
    <div v-if="results.length > 0 || status === 'done' || status === 'error'" class="results-panel">
      <ul
        v-if="results.length > 0"
        id="search-results-list"
        role="listbox"
        aria-label="Search results"
      >
        <li
          v-for="result in results"
          :key="result.itemId"
          role="option"
          tabindex="0"
          @click="select(result)"
          @keydown.enter="select(result)"
        >
          <span class="result-text">
            <strong>{{ result.itemName }}</strong>
            <span class="result-wpp">{{ wppName(result.groupId) }}</span>
          </span>
          <svg class="result-arrow" viewBox="0 0 24 24" width="14" height="14" aria-hidden="true">
            <path d="M5 12h14M13 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </li>
      </ul>
      <p v-else-if="status === 'done'" class="results-empty" role="status" aria-live="polite">
        No matches found.
      </p>
      <p v-else-if="status === 'error'" class="results-error" role="alert">
        Search unavailable. Please try again.
      </p>
    </div>
  </transition>
</template>

<script setup>
import { computed } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

const store = useStore();
const router = useRouter();
const results = computed(() => store.state.search.results);
const status = computed(() => store.state.search.status);
const groupNames = computed(() => store.state.corpus.ui.groupNames);

const wppName = (id) => groupNames.value[id] ?? `Group ${id}`;

async function select(result) {
  await store.dispatch('search/clear');
  await router.push({ query: { highlight: result.itemId } });
}
</script>

<style scoped>
.results-panel {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  right: 0;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  z-index: 200;
  max-height: 360px;
  overflow-y: auto;
  box-shadow:
    0 18px 38px -16px rgba(10, 10, 10, 0.18),
    0 2px 8px -2px rgba(10, 10, 10, 0.06);
  overflow: hidden;
}

ul {
  list-style: none;
  padding: 0.35rem;
  margin: 0;
  max-height: 360px;
  overflow-y: auto;
}

li {
  padding: 0.6rem 0.75rem;
  cursor: pointer;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  transition: background 0.18s var(--ease), color 0.18s var(--ease);
  color: var(--ink-2);
}

li:hover,
li:focus {
  background: var(--accent-soft);
  color: var(--accent);
  outline: none;
}

.result-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.result-text strong {
  font-size: 0.92rem;
  font-weight: 550;
  letter-spacing: -0.005em;
  color: var(--ink);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

li:hover .result-text strong,
li:focus .result-text strong {
  color: var(--accent);
}

.result-wpp {
  font-size: 0.72rem;
  color: var(--muted-2);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 500;
}

.result-arrow {
  color: var(--muted-2);
  flex-shrink: 0;
  transition: transform 0.2s var(--ease), color 0.2s var(--ease);
}

li:hover .result-arrow,
li:focus .result-arrow {
  color: var(--accent);
  transform: translateX(2px);
}

.results-empty,
.results-error {
  padding: 0.9rem 1rem;
  font-size: 0.85rem;
}

.results-empty { color: var(--muted); }
.results-error { color: #b91c1c; }

.results-pop-enter-active,
.results-pop-leave-active {
  transition: opacity 0.18s var(--ease), transform 0.18s var(--ease);
}

.results-pop-enter-from,
.results-pop-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
