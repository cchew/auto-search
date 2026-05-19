import { createStore } from 'vuex';
import search from './stores/search.js';

const corpus = {
  namespaced: true,
  state: () => ({
    items: [],
    ui: {
      appTitle: 'Auto Search',
      appLede: 'Semantic search.',
      suggestions: [],
      groupNames: {},
      idField: 'item_id',
      groupField: 'wpp_id',
      nameField: 'name',
      descriptionField: 'description',
      searchAriaLabel: 'Search',
    },
    loaded: false,
  }),
  mutations: {
    setItems(state, items) { state.items = items; },
    setUi(state, ui) { state.ui = { ...state.ui, ...ui }; },
    setLoaded(state, value) { state.loaded = value; },
  },
};

export default createStore({
  modules: { search, corpus },
});
