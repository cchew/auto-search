import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  base: '/modules/custom/autosearch/dist/',
  build: {
    outDir: '../drupal/modules/autosearch/dist',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'autosearch.js',
        chunkFileNames: 'autosearch.js',
        assetFileNames: (info) => info.name?.endsWith('.css') ? 'autosearch.css' : (info.name ?? 'asset'),
        manualChunks: () => 'autosearch',
      },
    },
  },
});
