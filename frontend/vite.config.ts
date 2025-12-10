import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Auth endpoints (login, signup)
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      // User profile and all /me/* routes (expenses, categories)
      '/me': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
