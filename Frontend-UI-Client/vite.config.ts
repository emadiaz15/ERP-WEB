import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  const isDev = mode === 'development'

  // Backend API target (extraer base URL sin /api/v1)
  const API_BASE = env.VITE_API_BASE_URL || 'http://localhost:8080/api/v1'
  const API_TARGET = API_BASE.replace(/\/api\/v1$/, '') || 'http://localhost:8080'

  return {
    plugins: [react()],
    server: {
      port: parseInt(env.VITE_PORT || '5173', 10),
      strictPort: true,
      proxy: isDev
        ? {
            // API REST
            '/api': {
              target: API_TARGET,
              changeOrigin: true,
              secure: false,
              ws: false,
            },
            // WebSocket
            '/ws': {
              target: API_TARGET.replace(/^http/, 'ws'),
              changeOrigin: true,
              ws: true,
            },
          }
        : undefined,
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
        '@/shared': path.resolve(__dirname, 'src/shared'),
        '@/features': path.resolve(__dirname, 'src/features'),
        '@/app': path.resolve(__dirname, 'src/app'),
      },
    },
    build: {
      outDir: 'dist',
      emptyOutDir: true,
      sourcemap: isDev,
    },
    base: '/',
  }
})
