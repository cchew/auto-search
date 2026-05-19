import { mount, flushPromises } from '@vue/test-utils';
import { createStore } from 'vuex';
import SearchBar from '../components/SearchBar.vue';
import searchModule from '../stores/search.js';

const corpusModule = {
  namespaced: true,
  state: () => ({
    items: [],
    ui: { searchAriaLabel: 'Search data items', groupNames: {} },
    loaded: false,
  }),
};

function mountBar(actionOverrides = {}) {
  const store = createStore({
    modules: {
      search: {
        ...searchModule,
        actions: { ...searchModule.actions, ...actionOverrides },
      },
      corpus: corpusModule,
    },
  });
  return { wrapper: mount(SearchBar, { global: { plugins: [store] } }), store };
}

describe('SearchBar', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.clearAllTimers();
    vi.useRealTimers();
  });
  it('dispatches search/query after 300ms debounce', async () => {
    const query = vi.fn();
    const { wrapper } = mountBar({ query, clear: vi.fn() });
    await wrapper.find('input').setValue('GP FTE');
    expect(query).not.toHaveBeenCalled();
    vi.advanceTimersByTime(300);
    await flushPromises();
    expect(query).toHaveBeenCalledWith(expect.anything(), 'GP FTE');
  });

  it('dispatches search/clear when input is emptied', async () => {
    const clear = vi.fn();
    const { wrapper } = mountBar({ clear, query: vi.fn() });
    await wrapper.find('input').setValue('');
    expect(clear).toHaveBeenCalled();
  });

  it('has role combobox and aria-label', () => {
    const { wrapper } = mountBar();
    const input = wrapper.find('input');
    expect(input.attributes('role')).toBe('combobox');
    expect(input.attributes('aria-label')).toBeTruthy();
  });
});
