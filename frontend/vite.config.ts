import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { defineConfig } from 'vite'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      'stream': 'stream-browserify',
      'events': 'events',
      'buffer': 'buffer'
    }
  },
  optimizeDeps: {
    include: ['stream-browserify', 'events', 'buffer']
  },
  server: {
    host: '0.0.0.0',
    port: 3002,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        ws: true,
        configure: (proxy, options) => {
          proxy.on('upgrade', (req, socket, head) => {
            const options = {
              target: 'http://localhost:8000',
              ws: true
            };
            proxy.ws(req, socket, head, options);
          });
        }
      },
      '/uploads': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false
  }
})
