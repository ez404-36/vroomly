import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react-swc';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';

export default defineConfig(({ mode }) => {
  // Папка, где лежит .env
  const rootEnvDir = path.resolve(__dirname, '..');

  // Подгружаем переменные из этой папки
  const env = loadEnv(mode, rootEnvDir, '');

  return {
    plugins: [tailwindcss(), react()],
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
