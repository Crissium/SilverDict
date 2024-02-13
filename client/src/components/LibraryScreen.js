import React from 'react';
import Stack from '@mui/material/Stack';
import { Outlet } from 'react-router-dom';
import Appbar from './Library/Appbar';

export default function LibraryScreen() {
	return (
		<Stack
			height='100vh'
			sx={{display: 'flex', flexDirection: 'column'}}
		>
			<Appbar />
			<Outlet />
		</Stack>
	);
}
