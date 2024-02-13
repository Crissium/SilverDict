import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import MenuButton from '../common/MenuButton';
import FtsInput from './FtsInput';

export default function AppBarDesktop() {
	return (
		<AppBar position='static' sx={{flexShrink: 1}}>
			<Toolbar variant='dense'>
				<MenuButton />
				<FtsInput />
			</Toolbar>
		</AppBar>
	);
}
