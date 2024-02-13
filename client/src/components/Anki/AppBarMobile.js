import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import MenuButton from '../common/MenuButton';
import AnkiInput from './AnkiInput';
import DictionariesButton from './DictionariesButton';

export default function AppBarMobile() {
	return (
		<AppBar position='static'>
			<Toolbar>
				<MenuButton />
				<AnkiInput />
				<DictionariesButton />
			</Toolbar>
		</AppBar>
	);
}