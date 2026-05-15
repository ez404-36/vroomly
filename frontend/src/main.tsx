import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';

import { ColorSchemeScript, MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';
import '@mantine/core/styles.css';
import '@mantine/dates/styles.css';
import '@mantine/notifications/styles.css';
import './fonts/fonts.css';
import './styles/global.css';

import { Provider } from 'react-redux';
import { store } from './store/store.ts';
import { theme } from './styles/theme.ts';
import { resolver } from './styles/resolver.ts';

import App from './components/App.tsx';

createRoot(document.getElementById('root')!).render(
  <Provider store={store}>
    <StrictMode>
      <BrowserRouter>
        <>
          <ColorSchemeScript defaultColorScheme="dark" />
          <MantineProvider theme={theme} cssVariablesResolver={resolver}>
              <Notifications />
              <App />
            </MantineProvider>
        </>
      </BrowserRouter>
    </StrictMode>
  </Provider>,
);
