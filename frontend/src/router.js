import { createRouter, createWebHashHistory } from 'vue-router';
import App from './App.vue';

export default createRouter({
  history: createWebHashHistory(),
  routes: [{ path: '/', component: App }],
});
