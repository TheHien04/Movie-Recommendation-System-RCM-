import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://127.0.0.1:5001',
      '/recommend': 'http://127.0.0.1:5001',
      '/movie': 'http://127.0.0.1:5001',
      '/random_movies': 'http://127.0.0.1:5001',
    },
  },
})
