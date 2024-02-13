import React from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogContentText from '@mui/material/DialogContentText';
import DialogTitle from '@mui/material/DialogTitle';
import { localisedStrings } from '../../l10n';

export default function FormDialogue(props) {
	const {
		opened,
		setOpened,
		title,
		content,
		originalValue,
		handleSubmittedData, // a function that takes a string and returns nothing
		inputType,
		placeholder,
		autoCapitalise
	} = props;

	function handleSubmit(e) {
		e.preventDefault();
		handleSubmittedData(e.target[0].value);
		setOpened(false);
	}

	return (
		<Dialog
			open={opened}
			onClose={() => setOpened(false)}
			fullWidth
			PaperProps={{
				component: 'form',
				onSubmit: handleSubmit
			}}
		>
			<DialogTitle>{title}</DialogTitle>
			<DialogContent>
				<DialogContentText>
					{content}
				</DialogContentText>
				<TextField
					margin='dense'
					placeholder={placeholder}
					type={inputType}
					defaultValue={originalValue}
					fullWidth
					autoComplete='off'
					inputProps={{
						autoCapitalize: autoCapitalise,
						autoCorrect: 'off',
						dir: 'auto'
					}}
				/>
			</DialogContent>
			<DialogActions>
				<Button onClick={() => setOpened(false)}>
					{localisedStrings['generic-cancel']}
				</Button>
				<Button
					type='submit'
				>
					{localisedStrings['generic-ok']}
				</Button>
			</DialogActions>
		</Dialog>
	);
}
