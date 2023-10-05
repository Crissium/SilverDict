import React, { useState } from 'react';
import ISO6391 from 'iso-639-1';
import { API_PREFIX } from '../config';
import { JSON_HEADER, loadDataFromJsonResponse, convertDictionarySnakeCaseToCamelCase, convertDictionaryCamelCaseToSnakeCase } from '../utils';
import { Dialogue } from './Dialogue';
import { EditGroupLangDialogue } from './EditGroupLangDialogue';
import { EditGroupNameDialogue } from './EditGroupNameDialogue';
import { AddGroupDialogue } from './AddGroupDialogue';

export function GroupManager(props) {
	const { dictionaries, setDictionaries, groups, setGroups, groupings, setGroupings } = props;

	const [groupInView, setGroupInView] = useState('Default Group');
	const [activeDictionaryIndex, setActiveDictionaryIndex] = useState(0);
	const [activeDictionaryInGroupViewIndex, setActiveDictionaryInGroupViewIndex] = useState(0);

	const [addGroupDialogueOpened, setAddGroupDialogueOpened] = useState(false);
	const [editNameDialogueOpened, setEditNameDialogueOpened] = useState(false);
	const [editLangDialogueOpened, setEditLangDialogueOpened] = useState(false);

	function move(index, direction) {
		const newDictionaries = [...dictionaries];

		// First we gotta find the index of the previous/next dictionary in the same group
		let swappedIndex = index + direction;
		while (swappedIndex >= 0 && swappedIndex < newDictionaries.length && !groupings[groupInView].includes(newDictionaries[swappedIndex].name)) {
			swappedIndex += direction;
		}
		if (swappedIndex < 0 || swappedIndex >= newDictionaries.length) {
			return;
		}

		[newDictionaries[index], newDictionaries[swappedIndex]] = [newDictionaries[swappedIndex], newDictionaries[index]];
		fetch(`${API_PREFIX}/management/dictionaries`, {
			method: 'PUT',
			headers: JSON_HEADER,
			body: JSON.stringify(newDictionaries.map(convertDictionaryCamelCaseToSnakeCase))
		})
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setDictionaries(data.map(convertDictionarySnakeCaseToCamelCase));
			})
			.catch((error) => {
				alert('Failed to move dictionary.');
			});
	}

	function getGroupWithName(name) {
		return groups.find((group) => group.name === name);
	}

	function addDictionaryToGroup() {
		const dictionaryName = dictionaries[activeDictionaryIndex].name;
		if (groupings[groupInView].includes(dictionaryName)) {
			alert('Dictionary already exists in this group.');
			return;
		}

		fetch(`${API_PREFIX}/management/dictionary_groupings`, {
			method: 'POST',
			headers: JSON_HEADER,
			body: JSON.stringify({ dictionary_name: dictionaryName, group_name: groupInView })
		})
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setGroupings(data);
			})
			.catch((error) => {
				alert('Failed to add dictionary to group.');
			});
	}

	function removeDictionaryFromGroup() {
		const dictionaryName = dictionaries[activeDictionaryInGroupViewIndex].name;
		if (!groupings[groupInView].includes(dictionaryName)) {
			alert('Dictionary does not exist in this group.');
			return;
		}

		fetch(`${API_PREFIX}/management/dictionary_groupings`, {
			method: 'DELETE',
			headers: JSON_HEADER,
			body: JSON.stringify({ dictionary_name: dictionaryName, group_name: groupInView })
		})
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setGroupings(data);
			})
			.catch((error) => {
				alert('Failed to remove dictionary from group.');
			});
	}

	function removeGroup() {
		fetch(`${API_PREFIX}/management/groups`, {
			method: 'DELETE',
			headers: JSON_HEADER,
			body: JSON.stringify({ name: groupInView })
		})
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setGroups(data['groups']);
				setGroupings(data['groupings']);
				setGroupInView(data['groups'][0].name);
			})
			.catch((error) => {
				alert('Failed to remove group.');
			});
	}

	return (
		<div id='group-manager'>
			<div id='all-dictionaries'>
				<label className='heading'><strong>All dictionaries:</strong></label>
				<ul>
					{dictionaries.map((dictionary, index) => {
						return (
							<li
								key={dictionary.name}
								className={`clickable ${index === activeDictionaryIndex ? 'active' : ''}`}
								onClick={() => setActiveDictionaryIndex(index)}
							>
								{dictionary.displayName}
							</li>
						);
					})}
				</ul>
			</div>
			<div id='group-manager-buttons'>
				<Dialogue
					id='dialogue-add-group'
					icon='+'
					opened={addGroupDialogueOpened}
					setOpened={setAddGroupDialogueOpened}
				>
					<AddGroupDialogue
						setGroups={setGroups}
						setGroupings={setGroupings}
						setDialogueOpened={setAddGroupDialogueOpened} />
				</Dialogue>
				<button onClick={() => addDictionaryToGroup()}>→</button>
				<button onClick={() => removeDictionaryFromGroup()}>←</button>
			</div>
			<div id='groups'>
				<div className='heading'>
					<select
						value={groupInView}
						onChange={(e) => setGroupInView(e.target.value)}
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
					{groupInView !== 'Default Group' &&
						<>
							<button onClick={() => removeGroup()}>✕</button>
							<Dialogue
								id='dialogue-edit-name'
								icon='✎'
								opened={editNameDialogueOpened}
								setOpened={setEditNameDialogueOpened}
							>
								<EditGroupNameDialogue
									originalName={groupInView}
									setGroups={setGroups}
									groupings={groupings}
									setGroupings={setGroupings}
									setGroupInView={setGroupInView}
									setDialogueOpened={setEditNameDialogueOpened} />
							</Dialogue>
						</>}
				</div>
				{groupInView !== 'Default Group' &&
				<>
					<label>Languages:</label>
					<Dialogue
						id='dialogue-edit-lang'
						icon='✎'
						opened={editLangDialogueOpened}
						setOpened={setEditLangDialogueOpened}
					>
						<EditGroupLangDialogue
							name={groupInView}
							setGroups={setGroups}
							setDialogueOpened={setEditLangDialogueOpened} />
					</Dialogue>
					<ul>
						{[...getGroupWithName(groupInView).lang].map((lang) => (
							<li id='lang-list-item' key={lang}>{ISO6391.getNativeName(lang)}</li>
						))}
					</ul>
				</>}
				
				<ul>
					{dictionaries.map((dictionary, index) => {
						if (groupings[groupInView].includes(dictionary.name)) {
							return (
								<li
									key={dictionary.name}
									className={`clickable ${index === activeDictionaryInGroupViewIndex ? 'active' : ''}`}
									onClick={() => setActiveDictionaryInGroupViewIndex(index)}
								>
									<button onClick={() => move(index, -1)}>↑</button>
									<button onClick={() => move(index, +1)}>↓</button>
									{dictionary.displayName}
								</li>
							);
						} else {
							return null;
						}
					})}
				</ul>
			</div>
		</div>
	);
}
