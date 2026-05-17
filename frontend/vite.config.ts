import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'
import { defineConfig, loadEnv } from 'vite'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd())
  
  // 从环境变量获取 API 基础地址，默认为 http://localhost:8084
  const apiBaseUrl = env.VITE_API_BASE_URL || process.env.VITE_API_BASE_URL || 'http://localhost:8084'

  return {
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
          target: apiBaseUrl,
          changeOrigin: true,
          secure: false,
          ws: true,
          configure: (proxy, options) => {
            proxy.on('upgrade', (req, socket, head) => {
              const options = {
                target: apiBaseUrl,
                ws: true
              };
              proxy.ws(req, socket, head, options);
            });
          }
        },
        '/uploads': {
          target: apiBaseUrl,
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
  }
})
