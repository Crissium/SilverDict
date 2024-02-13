import React from 'react';
import LinearProgress from '@mui/material/LinearProgress';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';

export default function ProgressDialogue(props) {
	const { opened, title } = props;

	return (
		<Dialog
			open={opened}
		>
			<DialogTitle>{title}</DialogTitle>
			<DialogContent>
				<LinearProgress />
			</DialogContent>
		</Dialog>
	);
}
