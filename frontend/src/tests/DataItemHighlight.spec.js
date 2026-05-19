import { mount } from '@vue/test-utils';
import { createRouter, createMemoryHistory } from 'vue-router';
import DataItemHighlight from '../components/DataItemHighlight.vue';

async function mountWithHighlight(highlightId) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/', component: { template: '<div/>' } }],
  });
  await router.push(highlightId ? `/?highlight=${highlightId}` : '/');
  return mount(DataItemHighlight, { global: { plugins: [router] } });
}

describe('DataItemHighlight', () => {
  it('adds search-highlight class to matching element', async () => {
    const el = document.createElement('div');
    el.setAttribute('data-item-id', '42');
    document.body.appendChild(el);

    try {
      await mountWithHighlight('42');
      await new Promise(r => setTimeout(r, 0));
      expect(el.classList.contains('search-highlight')).toBe(true);
    } finally {
      document.body.removeChild(el);
    }
  });

  it('does nothing when no highlight param', async () => {
    await expect(mountWithHighlight(null)).resolves.toBeTruthy();
  });

  it('does nothing when no element matches', async () => {
    await expect(mountWithHighlight('999')).resolves.toBeTruthy();
  });
});
