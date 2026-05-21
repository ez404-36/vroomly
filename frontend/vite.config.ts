import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react-swc';
import tailwindcss from '@tailwindcss/vite';
import svgr from 'vite-plugin-svgr';
import path from 'path';

export default defineConfig(({ mode }) => {
  const rootEnvDir = path.resolve(__dirname, '..');
  const env = loadEnv(mode, rootEnvDir, '');

  return {
    plugins: [
      tailwindcss(),
      svgr({
        exportAsDefault: false,
      }),
      react(),
    ],
    server: {
      host: true,
      port: 5173,
      strictPort: true,
      watch: {
        usePolling: env.VITE_USE_POLLING === 'true',
      },
    },
  };
});
