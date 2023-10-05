import React, { useEffect } from 'react';
import { API_PREFIX } from '../config';
import { JSON_HEADER, loadDataFromJsonResponse, convertDictionarySnakeCaseToCamelCase } from '../utils';

export function AddDictionaryDialogue(props) {
	const { group, dictionaries, setDictionaries, setGroupings, setDialogueOpened } = props;
	const [supportedFormats, setSupportedFormats] = React.useState([]);
	const [loadingFormats, setLoadingFormats] = React.useState(true);
	const [newDictionaryDisplayName, setNewDictionaryDisplayName] = React.useState('');
	const [newDictionaryFilename, setNewDictionaryFilename] = React.useState('');
	const [newDictionaryFormat, setNewDictionaryFormat] = React.useState('');

	useEffect(function () {
		fetch(`${API_PREFIX}/management/formats`)
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setSupportedFormats(data);
				setNewDictionaryFormat(data[0]);
				setLoadingFormats(false);
			});
	}, []);

	function getDictionaryName(filename) {
		return filename.split('/').pop().split('.')[0];
	}

	function addDictionary() {
		if (newDictionaryDisplayName.length === 0) {
			alert('Dictionary name cannot be empty.');
			return;
		}

		if (newDictionaryFilename.length === 0) {
			alert('Filename cannot be empty.');
			return;
		}

		if (supportedFormats.indexOf(newDictionaryFormat) === -1) {
			alert('Unsupported format.');
			return;
		}

		const dictionaryName = getDictionaryName(newDictionaryFilename);
		if (dictionaries.map((dictionary) => dictionary.name).indexOf(dictionaryName) !== -1) {
			alert('A dictionary with the same name already exists.');
			return;
		}

		const newDictionaryInfo = {
			dictionary_display_name: newDictionaryDisplayName,
			dictionary_name: dictionaryName,
			dictionary_format: newDictionaryFormat,
			dictionary_filename: newDictionaryFilename
		};

		fetch(`${API_PREFIX}/validator/dictionary_info`, {
			method: 'POST',
			headers: JSON_HEADER,
			body: JSON.stringify(newDictionaryInfo)
		})
			.then(loadDataFromJsonResponse)
			.then((data) => {
				if (data['valid']) {
					newDictionaryInfo['group_name'] = group;
					fetch(`${API_PREFIX}/management/dictionaries`, {
						method: 'POST',
						headers: JSON_HEADER,
						body: JSON.stringify(newDictionaryInfo)
					})
						.then(loadDataFromJsonResponse)
						.then((data) => {
							setDictionaries(data['dictionaries'].map(convertDictionarySnakeCaseToCamelCase));
							setGroupings(data['groupings']);
						})
						.catch((error) => {
							alert('Error adding dictionary.');
						});
				} else {
					alert('Invalid dictionary.');
				}
			})
			.catch((error) => {
				alert('Error validating dictionary. Please try again.');
			})
			.finally(() => {
				setDialogueOpened(false);
			})
	}

	if (loadingFormats)
		return (<div>Loading supported formats…</div>);

	else
		return (
			<>
				<label><strong>Dictionary name:</strong></label>
				<br />
				<input
					type='text'
					value={newDictionaryDisplayName}
					onChange={(e) => setNewDictionaryDisplayName(e.target.value)} />
				<br />
				<label>
					<strong>Filename</strong>(e.g.
					<br />
					<code>/home/alice/Documents/Dictionaries/dict.mdx</code>)
				</label>
				<br />
				<input
					type='text'
					value={newDictionaryFilename}
					onChange={(e) => setNewDictionaryFilename(e.target.value)} />
				<br />
				<label><strong>Format:</strong></label>
				<select
					value={newDictionaryFormat}
					onChange={(e) => setNewDictionaryFormat(e.target.value)}
				>
					{supportedFormats.map((format) => {
						return (
							<option
								key={format}
								value={format}
							>
								{format}
							</option>
						);
					})}
				</select>
				<button onClick={addDictionary}>Add</button>
			</>
		);
}
