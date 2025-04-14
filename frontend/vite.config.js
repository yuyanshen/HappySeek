import { defineConfig } from 'vite'

export default defineConfig({
  define: {
    'import.meta.env.VITE_WS_URL': JSON.stringify(process.env.VITE_WS_URL)
  }
})