/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface ImportMetaEnv {
  readonly VUE_APP_SUPABASE_URL: string
  readonly VUE_APP_SUPABASE_KEY: string
  readonly VUE_APP_DEEPSEEK_API_KEY: string
  readonly VUE_APP_COS_BUCKET: string
  readonly VUE_APP_COS_REGION: string
  readonly VUE_APP_SIGNATURE_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}