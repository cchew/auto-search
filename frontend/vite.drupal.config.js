import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';

// Build config for embedding the Vue SPA inside the Drupal autosearch module.
// Outputs to drupal/modules/autosearch/dist/ with deterministic filenames.
// The Drupal module volume-mounts that directory, so no image rebuild is needed after a rebuild here.
export default defineConfig({
  plugins: [vue()],
  base: '/modules/custom/autosearch/',
  build: {
    outDir: resolve(__dirname, '../../drupal/modules/autosearch/dist'),
    emptyOutDir: true,
    rollupOptions: {
      output: {
        entryFileNames: 'autosearch.js',
        chunkFileNames: 'autosearch-[name].js',
        assetFileNames: ({ name }) =>
          name && name.endsWith('.css') ? 'autosearch.css' : '[name][extname]',
      },
    },
  },
});
