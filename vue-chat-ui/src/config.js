// Configuración centralizada de endpoints de API
// En desarrollo local Vite utiliza el proxy ('') y en producción en la nube (Cloudflare)
// apunta directamente al backend desplegado en Render.
export const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? '' : 'https://tesis-simulador-transito-backend.onrender.com');

export const GOOGLE_CLIENT_ID = '704802332634-vi9ebc597pmdru4po6d5jrcm93o46ris.apps.googleusercontent.com';
