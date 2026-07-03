import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.VUE_APP_SUPABASE_URL || 'https://your-project.supabase.co'
const supabaseKey = process.env.VUE_APP_SUPABASE_KEY || 'your-anon-key'

export const supabase = createClient(supabaseUrl, supabaseKey)