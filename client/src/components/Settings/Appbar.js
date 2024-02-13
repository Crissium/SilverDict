import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import MenuButton from '../common/MenuButton';
import { localisedStrings } from '../../l10n';

export default function Appbar() {
	return (
		<AppBar position='static' sx={{flexShrink: 1}}>
			<Toolbar variant='dense'>
				<MenuButton />
				<Typography variant='h6' component='div'>
					{localisedStrings['settings-screen-title']}
				</Typography>
			</Toolbar>
		</AppBar>
	);
}
