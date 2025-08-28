import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Test environment configuration
export default defineConfig({
  plugins: [react()],
  define: {
    'process.env.NODE_ENV': '"production"',
    'process.env.VITE_API_BASE_URL': '"https://awade-backend-test.onrender.com"'
  },
  build: {
    outDir: 'dist-test',
    sourcemap: false,
    minify: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom']
        }
      }
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'https://awade-backend-test.onrender.com',
        changeOrigin: true,
        secure: true
      }
    }
  }
})
