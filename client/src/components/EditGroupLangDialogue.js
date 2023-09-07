import React, { useState } from 'react';
import { stringify } from 'yaml';
import ISO6391 from 'iso-639-1';
import { API_PREFIX } from '../config';
import { YAML_HEADER, loadDataFromYamlResponse, getSetFromLangString } from '../utils';

export function EditGroupLangDialogue(props) {
	const { name, setGroups, setDialogueOpened } = props;
	const [newLang, setNewLang] = useState(''); // comma-separated list of ISO 639-1 codes

	function editLang() {
		const langs = getSetFromLangString(newLang);
		for (const lang of langs) {
			if (!ISO6391.validate(lang)) {
				alert('Invalid language code found.');
				return;
			}
		}

		fetch(`${API_PREFIX}/management/group_lang`, {
			method: 'PUT',
			headers: YAML_HEADER,
			body: stringify({ name: name, lang: langs })
		})
			.then(loadDataFromYamlResponse)
			.then((data) => {
				setGroups(data);
			})
			.catch((error) => {
				alert('Failed to edit group languages.');
			})
			.finally(() => {
				setDialogueOpened(false);
			});
	}

	return (
		<>
			<label>
				Languages (comma separated <a href='https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes'>ISO 639-1</a> codes):
			</label>
			<br />
			<input
				type='text'
				value={newLang}
				onChange={(e) => setNewLang(e.target.value)} />
			<br />
			<button onClick={() => editLang()}>OK</button>
		</>
	);
}
