import React, { useState } from 'react';
import { API_PREFIX } from '../config';
import { JSON_HEADER, loadDataFromJsonResponse } from '../utils';

export function EditGroupNameDialogue(props) {
	const { originalName, setGroups, groupings, setGroupings, setGroupInView, setDialogueOpened } = props;
	const [newName, setNewName] = useState(originalName);

	function editName() {
		if (newName.length === 0) {
			alert('Group name cannot be empty.');
			return;
		}

		if (newName !== originalName && groupings[newName]) {
			alert('Group name already exists.');
			return;
		}

		fetch(`${API_PREFIX}/management/group_name`, {
			method: 'PUT',
			headers: JSON_HEADER,
			body: JSON.stringify({ old: originalName, new: newName })
		})
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setGroups(data['groups']);
				setGroupings(data['groupings']);
				setGroupInView(newName);
				setNewName('');
			})
			.catch((error) => {
				alert('Failed to edit group name.');
			})
			.finally(() => {
				setDialogueOpened(false);
			});
	}

	return (
		<>
			<label>New name:</label>
			<input
				type='text'
				value={newName}
				onChange={(e) => setNewName(e.target.value)} />
			<br />
			<button onClick={() => editName()}>OK</button>
		</>
	);
}
