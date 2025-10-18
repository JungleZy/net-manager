import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { fileURLToPath, URL } from 'node:url'

// 创建一个插件，在构建时将index.html中的bindType从'dev'修改为'prod'
function transformBindType() {
  return {
    name: 'transform-bind-type',
    enforce: 'pre',
    apply: 'build', // 只在构建时应用此插件
    transformIndexHtml(html, ctx) {
      if (ctx.filename && ctx.filename.endsWith('index.html')) {
        // 将bindType从'dev'改为'prod'
        return html.replace(
          /const\s+bindType\s*=\s*['"]dev['"]/g,
          `const bindType = 'prod'`
        )
      }
      return html
    }
  }
}

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    transformBindType(),
  ],
  // 设置基础路径为 /，应用部署在根路径
  base: '/',
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    }
  },
  server: {
    open: false,
    host: true,
    cors: true,
    port: 8001,
  },
  css: {
    postcss: './postcss.config.js',
    preprocessorOptions: {
      less: {
        javascriptEnabled: true,
      }
    },
    lightningcss: {
      // 禁用伪类/伪元素的警告
      errorRecovery: true,
    }
  },
  // 优化构建配置
  build: {
    rollupOptions: {
      output: {
        // 优化文件名
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
      }
    }
  }
})
