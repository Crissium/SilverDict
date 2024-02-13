import React from 'react';
import Dialog from '@mui/material/Dialog';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContentText from '@mui/material/DialogContentText';
import { localisedStrings } from '../../l10n';

export default function LoadingDialogue(props) {
	const { opened, setOpened, title } = props;

	return (
		<Dialog
			open={opened}
			onClose={() => setOpened(false)}
		>
			<DialogTitle>
				{title}
			</DialogTitle>
			<DialogContent>
				<DialogContentText>
					{localisedStrings['generic-loading']}
				</DialogContentText>
			</DialogContent>
		</Dialog>
	);
}
