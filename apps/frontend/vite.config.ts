import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '')
  
  // Determine the backend URL based on environment
  const isTest = mode === 'test' || env.VITE_ENVIRONMENT === 'test'
  const backendUrl = isTest 
    ? 'https://awade-backend-test.onrender.com'
    : (env.VITE_BACKEND_URL || 'http://localhost:8000')
  
  console.log(`🚀 Vite Config - Mode: ${mode}, Environment: ${env.VITE_ENVIRONMENT || 'development'}`)
  console.log(`🌐 Backend URL: ${backendUrl}`)
  console.log(`🧪 Is Test Environment: ${isTest}`)
  
  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    define: {
      'process.env.NODE_ENV': JSON.stringify(mode),
      'process.env.VITE_API_BASE_URL': JSON.stringify(env.VITE_API_BASE_URL || backendUrl),
      'process.env.VITE_BACKEND_URL': JSON.stringify(backendUrl),
      'process.env.VITE_ENVIRONMENT': JSON.stringify(env.VITE_ENVIRONMENT || mode),
    },
    server: {
      port: 3000,
      host: true,
      proxy: {
        '/api': {
          target: backendUrl,
          changeOrigin: true,
          secure: isTest,
        },
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: mode === 'development',
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            router: ['react-router-dom']
          }
        }
      }
    },
  }
}) 