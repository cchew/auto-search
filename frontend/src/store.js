import { createStore } from 'vuex';
import searchModule from './stores/search.js';

export default createStore({
  modules: {
    search: searchModule,
  },
});
