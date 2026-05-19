import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';

import './fonts/fonts.css';
import './styles/global.css';

import { Provider } from 'react-redux';
import { store } from './store/store.ts';
import { UIProvider } from './ui';

import App from './components/App.tsx';

// Initialize theme before first render
document.documentElement.setAttribute('data-theme', localStorage.getItem('color-scheme') ?? 'dark');

createRoot(document.getElementById('root')!).render(
  <Provider store={store}>
    <StrictMode>
      <BrowserRouter>
        <UIProvider>
          <App />
        </UIProvider>
      </BrowserRouter>
    </StrictMode>
  </Provider>,
);
