import React from 'react';
import { createRoot } from 'react-dom/client';
import CssBaseline from '@mui/material/CssBaseline';
import { ThemeProvider } from '@mui/material/styles';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import theme from './theme';

const rootElement = document.getElementById('root');
const root = createRoot(rootElement);

root.render(
	<ThemeProvider theme={theme}>
		<CssBaseline />
		<BrowserRouter basename={base_url}>
			<App />
		</BrowserRouter>
	</ThemeProvider>
);
