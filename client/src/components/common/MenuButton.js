import React from 'react';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import { useAppContext } from '../../AppContext';

export default function MenuButton() {
	const { setDrawerOpened } = useAppContext();

	return (
		<IconButton
			aria-label='menu'
			onClick={() => setDrawerOpened(true)}
		>
			<MenuIcon />
		</IconButton>
	);
}