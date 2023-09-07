import React, { useState } from 'react';
import { stringify } from 'yaml';
import { API_PREFIX, IS_SAFE_MODE } from '../config';
import { YAML_HEADER, loadDataFromYamlResponse, convertDictionarySnakeCaseToCamelCase } from '../utils';
import { Dialogue } from './Dialogue';
import { AddDictionaryDialogue } from './AddDictionaryDialogue';

export function DictionaryManager(props) {
	const { dictionaries, setDictionaries, groupings, setGroupings } = props;

	const [group, setGroup] = useState('Default Group');
	const [editedDictionaryIndex, setEditedDictionaryIndex] = useState(-1);
	const [newDisplayName, setNewDisplayName] = useState('');

	const [addDictionaryDialogueOpened, setAddDictionaryDialogueOpened] = useState(false);

	function deleteDictionary(name) {
		fetch(`${API_PREFIX}/management/dictionaries`, {
			method: 'DELETE',
			headers: YAML_HEADER,
			body: stringify({ name: name })
		})
			.then(loadDataFromYamlResponse)
			.then((data) => {
				setDictionaries(data['dictionaries'].map(convertDictionarySnakeCaseToCamelCase));
				setGroupings(data['groupings']);
			})
			.catch((error) => {
				alert('Failed to delete dictionary.');
			});
	}

	function handleEnterKeydown(e) {
		if (e.key === 'Enter') {
			fetch(`${API_PREFIX}/management/dictionary_name`, {
				method: 'PUT',
				headers: YAML_HEADER,
				body: stringify({ name: dictionaries[editedDictionaryIndex].name, display: newDisplayName })
			})
				.then(loadDataFromYamlResponse)
				.then((data) => {
					if (data['success']) {
						let newDictionaries = [...dictionaries];
						newDictionaries[editedDictionaryIndex].displayName = newDisplayName;
						setDictionaries(newDictionaries);
					} else {
						alert('Failed to update dictionary name.');
					}
					setEditedDictionaryIndex(-1);
					setNewDisplayName('');
				});
		}
	}

	return (
		<>
			<select
				value={group}
				onChange={(e) => setGroup(e.target.value)}
			>
				{Object.keys(groupings).map((group) => {
					return (
						<option
							key={group}
							value={group}
						>
							{group}
						</option>
					);
				})}
			</select>
			<Dialogue
				id='dialogue-add-dictionary'
				icon='+'
				opened={addDictionaryDialogueOpened}
				setOpened={setAddDictionaryDialogueOpened}
			>
				<AddDictionaryDialogue
					group={group}
					dictionaries={dictionaries}
					setDictionaries={setDictionaries}
					setGroupings={setGroupings}
					setDialogueOpened={setAddDictionaryDialogueOpened}
				/>
			</Dialogue>
			<ul>
				{dictionaries.map((dictionary, index) => {
					if (groupings[group].has(dictionary.name)) {
						return (
							<li
								key={index}
							>
								<button onClick={() => {
									setEditedDictionaryIndex(index);
									setNewDisplayName(dictionary.displayName);
								}}>
									✎
								</button>
								{IS_SAFE_MODE &&
								<button onClick={() => deleteDictionary(dictionary.name)}>
									✕
								</button>}
								{editedDictionaryIndex === index ?
									<input
										type='text'
										value={newDisplayName}
										onChange={(e) => setNewDisplayName(e.target.value)}
										onKeyDown={handleEnterKeydown} /> :
									dictionary.displayName}
							</li>
						);
					} else {
						return null;
					}
				})}
			</ul>
		</>
	);
}


