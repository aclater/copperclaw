import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api/operator': 'http://localhost:8000',
      '/api/stream': 'http://localhost:8090',
      '/api/state': 'http://localhost:8089'
    }
  }
})
