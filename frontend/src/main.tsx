import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import App from './components/App.tsx';
import { BrowserRouter } from 'react-router-dom';
import { ColorSchemeScript, MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css';
import { Provider } from 'react-redux';
import { store } from './store/store.ts';
import { theme } from './styles/theme.ts';

createRoot(document.getElementById('root')!).render(
  <Provider store={store}>
    <StrictMode>
      <BrowserRouter>
        <>
          <ColorSchemeScript defaultColorScheme="dark" />
          <MantineProvider theme={theme}>
            <App />
          </MantineProvider>
        </>
      </BrowserRouter>
    </StrictMode>
  </Provider>,
);
