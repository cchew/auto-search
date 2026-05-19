import { mount } from '@vue/test-utils';
import { createStore } from 'vuex';
import { createRouter, createMemoryHistory } from 'vue-router';
import SearchResults from '../components/SearchResults.vue';
import searchModule from '../stores/search.js';

const corpusModule = {
  namespaced: true,
  state: () => ({
    items: [],
    ui: { groupNames: { 1: 'GP Workforce' } },
    loaded: false,
  }),
};

function mountResults(stateOverrides = {}) {
  const store = createStore({
    modules: {
      search: { ...searchModule, state: () => ({ query: '', results: [], status: 'idle', ...stateOverrides }) },
      corpus: corpusModule,
    },
  });
  const router = createRouter({ history: createMemoryHistory(), routes: [{ path: '/', component: { template: '<div/>' } }] });
  return mount(SearchResults, { global: { plugins: [store, router] } });
}

describe('SearchResults', () => {
  it('renders item names when results exist', () => {
    const w = mountResults({ results: [{ groupId: 1, itemId: 1, itemName: 'GP FTE', score: 0.92 }], status: 'done' });
    expect(w.text()).toContain('GP FTE');
  });

  it('shows no-match message when done with empty results', () => {
    const w = mountResults({ results: [], status: 'done' });
    expect(w.text()).toContain('No matches found');
  });

  it('shows error message on error status', () => {
    const w = mountResults({ results: [], status: 'error' });
    expect(w.text()).toContain('Search unavailable');
  });

  it('renders listbox role when results exist', () => {
    const w = mountResults({ results: [{ groupId: 1, itemId: 1, itemName: 'GP FTE', score: 0.9 }], status: 'done' });
    expect(w.find('[role="listbox"]').exists()).toBe(true);
  });

  it('renders nothing when idle and no results', () => {
    const w = mountResults({ results: [], status: 'idle' });
    expect(w.text()).toBe('');
  });
});
