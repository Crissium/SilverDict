import React from 'react';
import Box from '@mui/material/Box';
import Articles from './Articles';

export default function ArticlesPane() {
	return (
		<Box
			width={0.3}
			height='100%'
			overflow='scroll'
			display='flex'
			flexDirection='column'
			padding='0.5em'
		>
			<Articles />
		</Box>
	);
}
