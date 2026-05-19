/** @typedef {'idle' | 'loading' | 'done' | 'error'} SearchStatus */
/** @typedef {'semantic' | 'keyword'} SearchMode */
/** @typedef {{ groupId: number, itemId: number, itemName: string, score: number }} SearchResultItem */

function readMode() {
  if (typeof window === 'undefined') return 'semantic';
  const search = (window.location.search || '').replace(/^\?/, '');
  const hash = window.location.hash || '';
  const hashQuery = hash.includes('?') ? hash.slice(hash.indexOf('?') + 1) : '';
  const params = new URLSearchParams([search, hashQuery].filter(Boolean).join('&'));
  return params.get('mode') === 'keyword' ? 'keyword' : 'semantic';
}

function keywordSearch(queryText, corpus, ui) {
  const q = queryText.toLowerCase().trim();
  const matches = [];
  for (const item of corpus) {
    const name = (item[ui.nameField] || '').toLowerCase();
    const idx = name.indexOf(q);
    if (idx >= 0) matches.push({ item, idx });
  }
  matches.sort((a, b) => a.idx - b.idx || a.item[ui.nameField].length - b.item[ui.nameField].length);
  return matches.slice(0, 5).map(({ item }) => ({
    groupId: item[ui.groupField],
    itemId: item[ui.idField],
    itemName: item[ui.nameField],
    score: 1,
  }));
}

export default {
  namespaced: true,

  state: () => ({
    /** @type {string} */ query: '',
    /** @type {SearchResultItem[]} */ results: [],
    /** @type {SearchStatus} */ status: 'idle',
    /** @type {SearchMode} */ mode: readMode(),
  }),

  mutations: {
    setQuery(state, query) { state.query = query; },
    setResults(state, results) { state.results = results; },
    setStatus(state, status) { state.status = status; },
    setMode(state, mode) { state.mode = mode; },
  },

  actions: {
    async query({ commit, state, rootState }, queryText) {
      if (!queryText || queryText.trim().length < 3) {
        commit('setResults', []);
        commit('setStatus', 'idle');
        return;
      }
      commit('setQuery', queryText);
      commit('setMode', readMode());

      if (state.mode === 'keyword') {
        commit('setStatus', 'loading');
        commit('setResults', keywordSearch(queryText, rootState.corpus.items, rootState.corpus.ui));
        commit('setStatus', 'done');
        return;
      }

      commit('setStatus', 'loading');
      try {
        const response = await fetch('/api/v1/search', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query: queryText, topK: 5 }),
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        commit('setResults', await response.json());
        commit('setStatus', 'done');
      } catch (err) {
        console.error('[search] query failed:', err);
        commit('setResults', []);
        commit('setStatus', 'error');
      }
    },

    clear({ commit }) {
      commit('setQuery', '');
      commit('setResults', []);
      commit('setStatus', 'idle');
    },
  },
};
