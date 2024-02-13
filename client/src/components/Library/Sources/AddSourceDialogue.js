import React from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import { useAppContext } from '../../../AppContext';
import { API_PREFIX } from '../../../config';
import { loadJson, JSON_HEADER } from '../../../utils';
import { localisedStrings } from '../../../l10n';

export default function AddSourceDialogue(props) {
	const { opened, setOpened } = props;
	const { setSources } = useAppContext();

	function handleSubmit(e) {
		e.preventDefault();

		const path = e.target.path.value;

		if (path.length === 0) {
			alert(localisedStrings['alert-empty-path']);
			return;
		}
		
		fetch(`${API_PREFIX}/validator/source`, {
			method: 'POST',
			headers: JSON_HEADER,
			body: JSON.stringify({ source: path })
		})
			.then(loadJson)
			.then((data) => {
				if (data['valid']) {
					fetch(`${API_PREFIX}/management/sources`, {
						method: 'POST',
						headers: JSON_HEADER,
						body: JSON.stringify({ source: path })
					})
						.then(loadJson)
						.then((data) => {
							setSources(data);
							setOpened(false);
						})
						.catch((error) => {
							alert(localisedStrings['failure-adding-source'] + '\n' + error);
						});
				} else {
					alert(localisedStrings['alert-invalid-source']);
				}
			})
			.catch((error) => {
				alert(localisedStrings['failure-validating-source'] + '\n' + error);
			});
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
			<DialogTitle>
				{localisedStrings['library-screen-add-source-dialogue-title']}
			</DialogTitle>
			<DialogContent>
				<TextField
					margin='dense'
					name='path'
					label={localisedStrings['library-screen-add-source-dialogue-textfield-path-label']}
					fullWidth
					autoComplete='off'
					inputProps={{
						autoCapitalize: 'off',
						autoCorrect: 'off',
						dir: 'auto'
					}}
				/>
			</DialogContent>
			<DialogActions>
				<Button
					onClick={() => setOpened(false)}
				>
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
