import { createApp } from 'vue';
import store from './store.js';
import router from './router.js';
import App from './App.vue';

async function bootstrap() {
  try {
    const [corpusRes, uiRes] = await Promise.all([
      fetch('/api/v1/corpus'),
      fetch('/api/v1/corpus/ui-config'),
    ]);
    if (!corpusRes.ok || !uiRes.ok) {
      throw new Error(`bootstrap fetch failed: corpus=${corpusRes.status}, ui=${uiRes.status}`);
    }
    const [items, ui] = await Promise.all([corpusRes.json(), uiRes.json()]);
    store.commit('corpus/setItems', items);
    store.commit('corpus/setUi', ui);
    store.commit('corpus/setLoaded', true);
  } catch (err) {
    console.error('[bootstrap] failed to load corpus/ui-config:', err);
  }

  createApp(App).use(store).use(router).mount('#app');
}

bootstrap();
