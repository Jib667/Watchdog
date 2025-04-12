import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Tell Vite to treat .webp files as static assets
  assetsInclude: ['**/*.webp', '**/*.png', '**/*.jpg', '**/*.jpeg', '**/*.gif'], 
  server: {
    // Optional: Server specific configurations like port
    port: 3000, 
    // Optional: Open browser automatically
    // open: true 
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path
      }
    }
  },
  build: {
    // Optional: Build specific configurations
    outDir: 'dist'
  }
})
