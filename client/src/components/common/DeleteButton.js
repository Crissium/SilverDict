import React from 'react';
import IconButton from '@mui/material/IconButton';
import DeleteIcon from '@mui/icons-material/Delete';

export default function DeleteButton(props) {
	const { handleClick } = props;

	return (
		<IconButton
			onClick={handleClick}
		>
			<DeleteIcon
				fontSize='small'
			/>
		</IconButton>
	);
}