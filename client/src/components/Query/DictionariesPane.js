import React from 'react';
import Box from '@mui/material/Box';
import Dictionaries from './Dictionaries';

export default function DictionariesPane() {
	return (
		<Box
			width={0.3}
			height='100%'
			overflow='scroll'
			display='flex'
			flexDirection='column'
			padding='0.5em'
		>
			<Dictionaries />
		</Box>
	);
}
