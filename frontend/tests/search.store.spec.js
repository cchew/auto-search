import { createStore } from 'vuex';
import searchModule from '../src/stores/search.js';

function makeStore() {
  return createStore({ modules: { search: searchModule } });
}

describe('search store', () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it('initial state is idle with empty results', () => {
    const store = makeStore();
    expect(store.state.search.status).toBe('idle');
    expect(store.state.search.results).toEqual([]);
    expect(store.state.search.query).toBe('');
  });

  it('query action sets done with results on success', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([{ wppId: 1, itemId: 1, itemName: 'GP FTE', score: 0.92 }]),
    });
    const store = makeStore();
    await store.dispatch('search/query', 'GP FTE');
    expect(store.state.search.status).toBe('done');
    expect(store.state.search.results[0].itemName).toBe('GP FTE');
    expect(store.state.search.query).toBe('GP FTE');
  });

  it('query action sets error on network failure', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('network error'));
    const store = makeStore();
    await store.dispatch('search/query', 'GP FTE');
    expect(store.state.search.status).toBe('error');
    expect(store.state.search.results).toEqual([]);
  });

  it('query action sets error on non-ok HTTP response', async () => {
    global.fetch = vi.fn().mockResolvedValue({ ok: false, status: 500 });
    const store = makeStore();
    await store.dispatch('search/query', 'GP FTE');
    expect(store.state.search.status).toBe('error');
  });

  it('query action is no-op for queries shorter than 3 chars', async () => {
    global.fetch = vi.fn();
    const store = makeStore();
    await store.dispatch('search/query', 'GP');
    expect(store.state.search.status).toBe('idle');
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('clear action resets to idle', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([{ wppId: 1, itemId: 1, itemName: 'GP FTE', score: 0.9 }]),
    });
    const store = makeStore();
    await store.dispatch('search/query', 'GP FTE');
    await store.dispatch('search/clear');
    expect(store.state.search.status).toBe('idle');
    expect(store.state.search.results).toEqual([]);
  });
});
