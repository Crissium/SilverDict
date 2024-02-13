import React from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import ISO6391 from 'iso-639-1';
import { useAppContext } from '../../../AppContext';
import { API_PREFIX } from '../../../config';
import { loadJson, JSON_HEADER, getSetFromLangString } from '../../../utils';
import { localisedStrings } from '../../../l10n';

export default function AddGroupDialogue(props) {
	const { opened, setOpened } = props;
	const { setGroups, groupings, setGroupings } = useAppContext();

	function handleSubmit(e) {
		e.preventDefault();

		const name = e.target.name.value;
		const langString = e.target.language.value;

		if (name.length === 0) {
			alert(localisedStrings['alert-empty-name']);
			return;
		}

		if (groupings[name]) {
			alert(localisedStrings['alert-duplicate-group']);
			return;
		}

		const langSet = getSetFromLangString(langString);
		for (const lang of langSet) {
			if (!ISO6391.validate(lang)) {
				alert(localisedStrings.formatString(
					localisedStrings['alert-invalid-language-code'],
					lang
				));
				return;
			}
		}
		
		fetch(`${API_PREFIX}/management/groups`, {
			method: 'POST',
			headers: JSON_HEADER,
			body: JSON.stringify({
				name,
				lang: Array.from(langSet)
			})
		})
			.then(loadJson)
			.then((data) => {
				setGroups(data['groups']);
				setGroupings(data['groupings']);
				setOpened(false);
			})
			.catch((error) => {
				alert(localisedStrings['failure-adding-group'] + '\n' + error);
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
				{localisedStrings['library-screen-add-group-dialogue-title']}
			</DialogTitle>
			<DialogContent>
				<TextField
					margin='dense'
					name='name'
					label={localisedStrings['library-screen-add-group-dialogue-textfield-name-label']}
					fullWidth
					autoComplete='off'
					inputProps={{
						autoCapitalize: 'on',
						autoCorrect: 'off',
						dir: 'auto'
					}}
				/>
				<TextField
					margin='dense'
					name='language'
					label={localisedStrings['library-screen-add-group-dialogue-textfield-lang-label']}
					helperText={localisedStrings['library-screen-add-group-dialogue-textfield-lang-helper']}
					placeholder='en, fr'
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
