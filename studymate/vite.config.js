import { defineConfig, loadEnv } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'
import { copyFileSync, existsSync } from 'fs'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.VITE_PROXY_TARGET || 'http://localhost:8002'

  return {
    plugins: [
      uni(),
      // Copy Cloudflare Pages runtime files (_redirects, _headers) to build output
      {
        name: 'copy-cloudflare-files',
        closeBundle() {
          const files = ['_redirects', '_headers']
          const publicDir = resolve(__dirname, 'public')
          const outDir = resolve(__dirname, 'dist/build/h5')
          for (const f of files) {
            const src = resolve(publicDir, f)
            const dest = resolve(outDir, f)
            if (existsSync(src)) {
              copyFileSync(src, dest)
              console.log(`[cloudflare] Copied ${f} to build output`)
            }
          }
          const workerSrc = resolve(__dirname, '_worker.js')
          const workerDest = resolve(outDir, '_worker.js')
          if (existsSync(workerSrc)) {
            copyFileSync(workerSrc, workerDest)
            console.log(`[cloudflare] Copied _worker.js to build output`)
          }
        }
      }
    ],
    define: {
      'process.env': {}
    },
    server: {
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true
        }
      }
    },
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: `@import "@/styles/variables.scss";`
        }
      }
    }
  }
})