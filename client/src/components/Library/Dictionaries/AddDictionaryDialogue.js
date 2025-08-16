import React, { useState } from 'react';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import MenuItem from '@mui/material/MenuItem';
import LoadingDialogue from '../../common/LoadingDialogue';
import { API_PREFIX } from '../../../config';
import { JSON_HEADER, loadJson, dictionarySnake2Camel } from '../../../utils';
import { useAppContext } from '../../../AppContext';
import { localisedStrings } from '../../../l10n';

export default function AddDictionaryDialogue(props) {
	const { opened, setOpened } = props;
	const { formats, dictionaries, setDictionaries, groups, setGroupings } = useAppContext();
	const [submitting, setSubmitting] = useState(false);

	function handleSubmit(e) {
		e.preventDefault();
		if (submitting)
		{
			return;
		}
		setSubmitting(true);
		
		const displayName = e.target.name.value;
		const filename = e.target.filename.value;
		const format = e.target.format.value;
		const groupName = e.target.groupName.value;
		
		if (displayName.length === 0) {
			alert(localisedStrings['alert-empty-name']);
			setSubmitting(false);
			return;
		}

		if (dictionaries.map((d) => d.displayName).includes(displayName)) {
			alert(localisedStrings['alert-duplicate-dictionary']);
			setSubmitting(false);
			return;
		}

		if (filename.length === 0) {
			alert(localisedStrings['alert-empty-filename']);
			setSubmitting(false);
			return;
		}

		const pathSep = filename.includes('/') ? '/' : '\\';
		const name = filename.split(pathSep).pop().split('.')[0];

		if (dictionaries.map((d) => d.name).includes(name)) {
			alert(localisedStrings['alert-duplicate-dictionary']);
			setSubmitting(false);
			return;
		}

		const newDict = {
			dictionary_display_name: displayName,
			dictionary_name: name,
			dictionary_format: format,
			dictionary_filename: filename
		};

		fetch(`${API_PREFIX}/validator/dictionary_info`, {
			method: 'POST',
			headers: JSON_HEADER,
			body: JSON.stringify(newDict)
		})
			.then(loadJson)
			.then((response) => {
				if (response.valid) {
					newDict['group_name'] = groupName;
					fetch(`${API_PREFIX}/management/dictionaries`, {
						method: 'POST',
						headers: JSON_HEADER,
						body: JSON.stringify(newDict)
					})
						.then(loadJson)
						.then((data) => {
							setDictionaries(data.dictionaries.map(dictionarySnake2Camel));
							setGroupings(data.groupings);
							setOpened(false);
							setSubmitting(false);
						})
						.catch((error) => {
							alert(localisedStrings['failure-adding-dictionary'] + '\n' + error);
							setSubmitting(false);
						});
				} else {
					alert(localisedStrings['alert-invalid']);
					setSubmitting(false);
				}
			})
			.catch((error) => {
				alert(localisedStrings['failure-validating-dictionary'] + '\n' + error);
				setSubmitting(false);
			});
	}

	if (formats[0] && groups[0] && groups[0].name)
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
					{localisedStrings['library-screen-add-dictionary-dialogue-title']}
				</DialogTitle>
				<DialogContent>
					<TextField
						margin='dense'
						name='name'
						label={localisedStrings['library-screen-dictionaries-table-head-name']}
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
						name='filename'
						label={localisedStrings['library-screen-dictionaries-table-head-filename']}
						placeholder='~/Documents/Dicts/sample.ifo'
						fullWidth
						autoComplete='off'
						inputProps={{
							autoCapitalize: 'off',
							autoCorrect: 'off',
							dir: 'auto'
						}}
					/>
					<TextField
						margin='dense'
						name='format'
						label={localisedStrings['library-screen-add-dictionary-dialogue-textfield-format-label']}
						fullWidth
						select
						defaultValue={formats[0]}
					>
						{formats.map((format, index) => (
							<MenuItem
								key={index}
								value={format}
							>
								{format}
							</MenuItem>
						))}
					</TextField>
					<TextField
						margin='dense'
						name='groupName'
						label={localisedStrings['library-screen-add-dictionary-dialogue-textfield-group-label']}
						helperText={localisedStrings['library-screen-add-dictionary-dialogue-textfield-group-helper']}
						fullWidth
						select
						defaultValue={groups[0].name}
					>
						{groups.map((group, index) => (
							<MenuItem
								key={index}
								value={group.name}
							>
								{group.name}
							</MenuItem>
						))}
					</TextField>
				</DialogContent>
				<DialogActions>
					<Button
						onClick={() => setOpened(false)}
						disabled={submitting}
					>
						{localisedStrings['generic-cancel']}
					</Button>
					<Button
						type='submit'
						disabled={submitting}
					>
						{localisedStrings['generic-ok']}
					</Button>
				</DialogActions>
			</Dialog>
		);
	else
		return (
			<LoadingDialogue
				opened={opened}
				setOpened={setOpened}
				title={localisedStrings['library-screen-add-dictionary-dialogue-title']}
			/>
		);
}
