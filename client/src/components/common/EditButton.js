import React from 'react';
import IconButton from '@mui/material/IconButton';
import EditIcon from '@mui/icons-material/Edit';

export default function EditButton(props) {
	const { handleClick } = props;

	return (
		<IconButton
			onClick={handleClick}
		>
			<EditIcon
				fontSize='small'
			/>
		</IconButton>
	);
}