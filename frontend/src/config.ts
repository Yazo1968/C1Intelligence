export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
export const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL ?? '';
export const SUPABASE_PUBLISHABLE_KEY = import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY ?? '';

if (!SUPABASE_URL || !SUPABASE_PUBLISHABLE_KEY) {
  console.error('Missing VITE_SUPABASE_URL or VITE_SUPABASE_PUBLISHABLE_KEY environment variables.');
}
