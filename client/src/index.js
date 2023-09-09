import React from 'react';
import ReactDOM from 'react-dom/client';
import DesktopApp from './DesktopApp';
import MobileApp from './MobileApp'
import './common.css'

const root = ReactDOM.createRoot(document.getElementById('root'));

const isMobile = window.innerWidth < 768;
if (isMobile) {
	import('./MobileApp.css');
} else {
	import('./DesktopApp.css')
}

root.render(
	(isMobile ? <MobileApp /> : <DesktopApp />)
);
