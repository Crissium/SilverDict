import React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { localisedStrings } from '../../l10n';

export default function ConfirmationDialogue(props) {
	const { opened, setOpened, title, content, onConfirm } = props;

	return (
		<Dialog
			open={opened}
			onClose={() => setOpened(false)}
		>
			<DialogTitle>{title}</DialogTitle>
			<DialogContent>
				<DialogContentText>
					{content}
				</DialogContentText>
			</DialogContent>
			<DialogActions>
				<Button onClick={() => setOpened(false)}>
					{localisedStrings['generic-no']}
				</Button>
				<Button
					onClick={() => {
						setOpened(false);
						onConfirm();
					}}
				>
					{localisedStrings['generic-yes']}
				</Button>
			</DialogActions>
		</Dialog>
	);
}
