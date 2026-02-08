import path from 'path';
import { fileURLToPath } from 'url';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, '.', '');
    return {
      server: {
        port: 3000,
        host: '0.0.0.0',
      },
      plugins: [react()],
      define: {
        'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
        'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY)
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, './src'),
        }
      },
      build: {
        // 代码分割策略
        rollupOptions: {
          output: {
            manualChunks: {
              // 将 React 相关库打包到单独的 chunk
              'react-vendor': ['react', 'react-dom', 'react-router-dom'],
              // 将状态管理库打包到单独的 chunk
              'state-vendor': ['zustand'],
              // 将 UI 库打包到单独的 chunk
              'ui-vendor': ['lucide-react'],
            }
          }
        },
        // 设置 chunk 大小警告限制
        chunkSizeWarningLimit: 1000,
        // 启用 CSS 代码分割
        cssCodeSplit: true,
        // 使用 esbuild 压缩（默认，无需额外依赖）
        minify: 'esbuild',
      },
      // 优化依赖预构建
      optimizeDeps: {
        include: ['react', 'react-dom', 'react-router-dom', 'zustand', 'lucide-react'],
      }
    };
});
