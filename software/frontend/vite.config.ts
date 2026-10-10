import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
    // Docker Desktop bind mounts can miss native file-change events.
    watch: { usePolling: true },
    proxy: {
      '/api': 'http://backend:8000',
    },
  },
});
