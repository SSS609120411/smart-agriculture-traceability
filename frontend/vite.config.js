import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  // 相对路径，兼容 GitHub Pages 子路径部署
  base: './',
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:5000', changeOrigin: true },
      '/static': { target: 'http://127.0.0.1:5000', changeOrigin: true }
    }
  }
})
