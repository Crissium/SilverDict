import React, { useState } from 'react';
import ISO6391 from 'iso-639-1';
import { API_PREFIX } from '../config';
import { JSON_HEADER, loadDataFromJsonResponse, getSetFromLangString } from '../utils';

export function AddGroupDialogue(props) {
	const { setGroups, setGroupings, setDialogueOpened } = props;
	const [newGroupName, setNewGroupName] = useState('');
	const [newGroupLang, setNewGroupLang] = useState(''); // comma-separated list of ISO 639-1 codes

	function addGroup() {
		if (newGroupName.length === 0) {
			alert('Group name cannot be empty.');
			return;
		}
		const langs = getSetFromLangString(newGroupLang);
		for (const lang of langs) {
			if (!ISO6391.validate(lang)) {
				alert('Invalid language code found.');
				return;
			}
		}
		const newGroup = {
			name: newGroupName,
			lang: Array.from(langs)
		};
		fetch(`${API_PREFIX}/management/groups`, {
			method: 'POST',
			headers: JSON_HEADER,
			body: JSON.stringify(newGroup)
		})
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setGroups(data['groups']);
				setGroupings(data['groupings']);
				setNewGroupName('');
				setNewGroupLang('');
			})
			.catch((error) => {
				alert('Failed to add group.');
			})
			.finally(() => {
				setDialogueOpened(false);
			});
	}

	return (
		<>
			<label>Group name:</label>
			<br />
			<input
				type='text'
				value={newGroupName}
				onChange={(e) => setNewGroupName(e.target.value)} />
			<br />
			<label>
				Languages (comma separated <a href='https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes'>ISO 639-1</a> codes):
			</label>
			<br />
			<input
				type='text'
				value={newGroupLang}
				onChange={(e) => setNewGroupLang(e.target.value)} />
			<br />
			<button onClick={() => addGroup()}>Add</button>
		</>
	);
}
