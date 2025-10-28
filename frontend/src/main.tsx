import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './styles/index.css';
import App from './components/App.tsx';
import { BrowserRouter } from 'react-router-dom';
import { createTheme, MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css';

const theme = createTheme({
  fontFamily: 'Open Sans, sans-serif',
  primaryColor: 'cyan',
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <MantineProvider theme={theme} defaultColorScheme="dark">
        <App />
      </MantineProvider>
    </BrowserRouter>
  </StrictMode>,
);
