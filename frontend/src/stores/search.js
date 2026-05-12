/** @typedef {'idle' | 'loading' | 'done' | 'error'} SearchStatus */
/** @typedef {{ wppId: number, itemId: number, itemName: string, score: number }} SearchResultItem */

export default {
  namespaced: true,

  state: () => ({
    /** @type {string} */ query: '',
    /** @type {SearchResultItem[]} */ results: [],
    /** @type {SearchStatus} */ status: 'idle',
  }),

  mutations: {
    setQuery(state, query) { state.query = query; },
    setResults(state, results) { state.results = results; },
    setStatus(state, status) { state.status = status; },
  },

  actions: {
    async query({ commit }, queryText) {
      if (!queryText || queryText.trim().length < 3) {
        commit('setResults', []);
        commit('setStatus', 'idle');
        return;
      }
      commit('setQuery', queryText);
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
