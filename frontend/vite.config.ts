import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // --- NOWA SEKCJA: NAPRAWA DLA DOCKERA NA WINDOWS ---
  server: {
    host: true,       // Pozwala na dostęp z zewnątrz kontenera (0.0.0.0)
    port: 5173,       // Wymusza port 3000
    strictPort: true, // Jeśli port 3000 zajęty, wywal błąd (zamiast szukać innego)
    watch: {
      usePolling: true // Wymagane na Windows, żeby działało odświeżanie zmian (Hot Reload)
    }
  },

  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, 'index.html'),
        login: resolve(__dirname, 'login.html'),
        register: resolve(__dirname, 'register.html'),
        dashboard: resolve(__dirname, 'dashboard.html'),
      },
    },
  },
})