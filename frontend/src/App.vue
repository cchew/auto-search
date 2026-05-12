<template>
  <div class="app">
    <header class="app-header">
      <div class="header-inner">
        <div class="eyebrow">
          <span class="eyebrow-dot" aria-hidden="true"></span>
          Workforce Planning Reports
          <span class="mode-badge" :class="`mode-badge--${mode}`">
            {{ mode === 'keyword' ? 'Keyword search' : 'Semantic search' }}
          </span>
        </div>
        <h1>Find the data item you need. Fast.</h1>
        <p class="lede">
          Semantic search across 14 report sets. Type in plain English; we'll
          locate the underlying data items.
        </p>

        <div class="search-wrapper">
          <SearchBar />
          <SearchResults />
        </div>

        <div class="suggestions">
          <span class="suggestions-label">Try</span>
          <button
            v-for="phrase in suggestions"
            :key="phrase"
            class="suggestion-chip"
            @click="useSuggestion(phrase)"
          >{{ phrase }}</button>
        </div>
      </div>
    </header>

    <main class="app-main">
      <DataItemHighlight>
        <section v-for="wpp in wpps" :key="wpp.id" class="wpp-section">
          <header class="wpp-header">
            <h2>{{ wpp.name }}</h2>
            <span class="wpp-count">{{ wpp.items.length }}<span class="wpp-count-label"> items</span></span>
          </header>
          <ul class="wpp-list">
            <li
              v-for="item in wpp.items"
              :key="item.id"
              :data-item-id="item.id"
              class="data-item"
            >
              <strong>{{ item.name }}</strong>
              <p>{{ item.description }}</p>
            </li>
          </ul>
        </section>
      </DataItemHighlight>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useStore } from 'vuex';
import SearchBar from '../components/SearchBar.vue';
import SearchResults from '../components/SearchResults.vue';
import DataItemHighlight from '../components/DataItemHighlight.vue';
import corpus from '../../test-harness/data/corpus.json';

const store = useStore();
const mode = computed(() => store.state.search.mode);

const suggestions = [
  'Primary care doctor staffing levels',
  'How many aged care staff are we employing?',
  'public hospital medical officer staffing levels',
  'regional breakdown of unnecessary hospital admissions',
];

function useSuggestion(phrase) {
  store.dispatch('search/query', phrase);
}

const REPORT_SET_NAMES = {
  1: 'GP Workforce', 2: 'Nursing Workforce', 3: 'Allied Health',
  4: 'Workforce Distribution', 5: 'Training Pipeline', 6: 'Mental Health Workforce',
  7: 'Aged Care Workforce', 8: 'Hospital Workforce', 9: 'Indigenous Health Workforce',
  10: 'Workforce Supply & Demand', 11: 'Chronic Disease Burden',
  12: 'Community Pharmacy', 13: 'Maternity Workforce', 14: 'Digital Health Adoption',
};

const wpps = computed(() => {
  const map = new Map();
  for (const item of corpus) {
    if (!map.has(item.wpp_id)) {
      map.set(item.wpp_id, { id: item.wpp_id, name: REPORT_SET_NAMES[item.wpp_id] ?? `Report Set ${item.wpp_id}`, items: [] });
    }
    map.get(item.wpp_id).items.push({ id: item.item_id, name: item.name, description: item.description ?? '' });
  }
  return [...map.values()].sort((a, b) => a.id - b.id);
});
</script>

<style>
:root {
  --bg: #fafafa;
  --surface: #ffffff;
  --ink: #0a0a0a;
  --ink-2: #27272a;
  --muted: #52525b;
  --muted-2: #71717a;
  --line: #e4e4e7;
  --line-soft: #f1f1f4;
  --accent: #1d4ed8;
  --accent-soft: #eff6ff;
  --accent-ring: rgba(29, 78, 216, 0.18);
  --radius: 14px;
  --radius-sm: 10px;
  --ease: cubic-bezier(0.16, 1, 0.3, 1);
  --font-display: 'Outfit', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif;
  --font-body: 'Outfit', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, SFMono-Regular, Menlo, monospace;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body {
  background: var(--bg);
  color: var(--ink);
  font-family: var(--font-body);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-feature-settings: 'ss01', 'cv11';
}

.app {
  min-height: 100dvh;
}

/* ---------- Header / Hero ---------- */

.app-header {
  background: var(--surface);
  border-bottom: 1px solid var(--line);
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: saturate(140%) blur(8px);
  background: color-mix(in srgb, var(--surface) 88%, transparent);
}

.header-inner {
  max-width: 1100px;
  margin: 0 auto;
  padding: 2.25rem 2rem 1.5rem;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.72rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--muted);
  margin-bottom: 0.85rem;
}

.mode-badge {
  margin-left: 0.6rem;
  font-size: 0.65rem;
  font-weight: 500;
  letter-spacing: 0.08em;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  border: 1px solid var(--line);
  text-transform: uppercase;
}

.mode-badge--semantic {
  background: var(--accent-soft);
  border-color: color-mix(in srgb, var(--accent) 30%, var(--line));
  color: var(--accent);
}

.mode-badge--keyword {
  background: #fef3c7;
  border-color: #fcd34d;
  color: #92400e;
}

.eyebrow-dot {
  width: 6px;
  height: 6px;
  border-radius: 999px;
  background: var(--accent);
  box-shadow: 0 0 0 4px var(--accent-soft);
  animation: pulse 2.4s var(--ease) infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}

.app-header h1 {
  font-family: var(--font-display);
  font-size: clamp(1.75rem, 3.4vw, 2.6rem);
  font-weight: 600;
  letter-spacing: -0.025em;
  line-height: 1.02;
  color: var(--ink);
  max-width: 22ch;
  margin-bottom: 0.6rem;
}

.lede {
  font-size: 0.95rem;
  color: var(--muted);
  line-height: 1.55;
  max-width: 52ch;
  margin-bottom: 1.4rem;
}

/* ---------- Search ---------- */

.search-wrapper {
  position: relative;
  max-width: 560px;
}

.suggestions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.9rem;
  max-width: 760px;
}

.suggestions-label {
  font-size: 0.7rem;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: var(--muted-2);
  padding-right: 0.25rem;
}

.suggestion-chip {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--ink-2);
  cursor: pointer;
  font: inherit;
  font-size: 0.78rem;
  font-weight: 450;
  padding: 0.35rem 0.85rem;
  transition: background 0.25s var(--ease), border-color 0.25s var(--ease), transform 0.15s var(--ease), color 0.25s var(--ease);
}

.suggestion-chip:hover {
  background: var(--accent-soft);
  border-color: color-mix(in srgb, var(--accent) 30%, var(--line));
  color: var(--accent);
}

.suggestion-chip:active {
  transform: translateY(-1px);
}

.suggestion-chip:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px var(--accent-ring);
}

/* ---------- Main ---------- */

.app-main {
  padding: 3rem 2rem 5rem;
  max-width: 1100px;
  margin: 0 auto;
}

.wpp-section {
  margin-bottom: 3rem;
}

.wpp-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  padding-bottom: 0.6rem;
  margin-bottom: 0.25rem;
  border-bottom: 1px solid var(--line);
}

.wpp-header h2 {
  font-family: var(--font-display);
  font-size: 1.05rem;
  font-weight: 600;
  letter-spacing: -0.01em;
  color: var(--ink);
}

.wpp-count {
  font-family: var(--font-mono);
  font-size: 0.78rem;
  color: var(--muted-2);
  font-variant-numeric: tabular-nums;
}

.wpp-count-label {
  font-family: var(--font-body);
  letter-spacing: 0.02em;
}

.wpp-list {
  list-style: none;
  display: grid;
  grid-template-columns: 1fr;
}

@media (min-width: 768px) {
  .wpp-list {
    grid-template-columns: 1fr 1fr;
    column-gap: 2.5rem;
  }
}

.data-item {
  padding: 0.95rem 0;
  border-bottom: 1px solid var(--line-soft);
  transition: background 0.4s var(--ease), box-shadow 0.4s var(--ease), padding-left 0.4s var(--ease);
  border-radius: 6px;
}

.data-item strong {
  display: block;
  margin-bottom: 0.2rem;
  font-size: 0.92rem;
  font-weight: 550;
  color: var(--ink);
  letter-spacing: -0.005em;
}

.data-item p {
  font-size: 0.82rem;
  color: var(--muted);
  line-height: 1.5;
  max-width: 60ch;
}

/* ---------- Highlight (used by DataItemHighlight.vue) ---------- */

.search-highlight {
  background: var(--accent-soft);
  box-shadow:
    inset 3px 0 0 var(--accent),
    0 0 0 1px var(--accent-ring);
  padding-left: 0.9rem !important;
  animation: highlight-in 0.5s var(--ease);
}

@keyframes highlight-in {
  from {
    background: color-mix(in srgb, var(--accent-soft) 0%, transparent);
    box-shadow: inset 0 0 0 var(--accent), 0 0 0 0 var(--accent-ring);
  }
}

/* ---------- Mobile ---------- */

@media (max-width: 640px) {
  .header-inner { padding: 1.5rem 1.25rem 1rem; }
  .app-main { padding: 2rem 1.25rem 4rem; }
}
</style>
