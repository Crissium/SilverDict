import React, { useState, useEffect } from 'react';
import { API_PREFIX } from '../config';
import { JSON_HEADER, loadDataFromJsonResponse, convertDictionarySnakeCaseToCamelCase } from '../utils';

export function Settings(props) {
	const { historySize, setHistorySize, setHistory, setDictionaries, setGroupings, suggestionsSize, setSuggestionsSize } = props;
	const [editingHistorySize, setEditingHistorySize] = useState(false);
	const [newHistorySize, setNewHistorySize] = useState(historySize);
	const [editingSuggestionsSize, setEditingSuggestionsSize] = useState(false);
	const [newSuggestionsSize, setNewSuggestionsSize] = useState(suggestionsSize);
	const [sources, setSources] = useState([]);
	const [loadingSources, setLoadingSources] = useState(true);
	const [newSource, setNewSource] = useState('');

	useEffect(function () {
		fetch(`${API_PREFIX}/management/sources`)
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setSources(data);
				setLoadingSources(false);
			});
	}, []);

	function handleHistorySizeChange() {
		setNewHistorySize(newHistorySize < 0 ? 0 : newHistorySize);
		fetch(`${API_PREFIX}/management/history_size`, {
			method: 'PUT',
			headers: JSON_HEADER,
			body: JSON.stringify({ size: newHistorySize })
		})
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setHistory(data);
				setHistorySize(newHistorySize);
			})
			.catch((error) => {
				alert('Failed to update history size.');
			})
			.finally(() => {
				setEditingHistorySize(false);
			});
	}

	function handleSuggestionsSizeChange() {
		setNewSuggestionsSize(newSuggestionsSize < 1 ? 1 : newSuggestionsSize);
		fetch(`${API_PREFIX}/management/num_suggestions`, {
			method: 'PUT',
			headers: JSON_HEADER,
			body: JSON.stringify({ size: newSuggestionsSize })
		})
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setSuggestionsSize(data['size']);
			})
			.catch((error) => {
				alert('Failed to update suggestions size.');
			})
			.finally(() => {
				setEditingSuggestionsSize(false);
			});
	}

	function rescanSources() {
		fetch(`${API_PREFIX}/management/scan`)
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setDictionaries(data['dictionaries'].map(convertDictionarySnakeCaseToCamelCase));
				setGroupings(data['groupings']);
			})
			.catch((error) => {
				alert('Failed to rescan sources.');
			});
	}

	function recreateNgramTable() {
		fetch(`${API_PREFIX}/management/create_ngram_table`)
			.then(loadDataFromJsonResponse)
			.then((data) => {
				if (data['success'])
					alert('Recreated ngram table.');
			})
			.catch((error) => {
				alert('Failed to recreate ngram table.');
			});
	}

	function addSource() {
		if (newSource.length === 0) {
			alert('Source cannot be empty.');
			return;
		}

		fetch(`${API_PREFIX}/validator/source`, {
			method: 'POST',
			headers: JSON_HEADER,
			body: JSON.stringify({ source: newSource })
		})
			.then(loadDataFromJsonResponse)
			.then((data) => {
				if (data['valid']) {
					fetch(`${API_PREFIX}/management/sources`, {
						method: 'POST',
						headers: JSON_HEADER,
						body: JSON.stringify({ source: newSource })
					})
						.then(loadDataFromJsonResponse)
						.then((data) => {
							setSources(data);
							setNewSource('');
						})
						.catch((error) => {
							alert('Failed to add source.');
						});
				} else {
					alert('Source is invalid.');
				}
			});
	}

	function removeSource(source) {
		fetch(`${API_PREFIX}/management/sources`, {
			method: 'DELETE',
			headers: JSON_HEADER,
			body: JSON.stringify({ source: source })
		})
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setSources(data);
			})
			.catch((error) => {
				alert('Failed to remove source.');
			});
	}

	return (
		<>
			<label>
				<strong>History size (≤ 0 to disable):</strong>
			</label>
			<br />
			{editingHistorySize ?
				<div id='history-size-edit-container'>
					<input
						id='history-size-edit-input'
						type='number'
						value={newHistorySize}
						onChange={(e) => setNewHistorySize(e.target.value)} />
					<button id='history-size-edit-button' onClick={handleHistorySizeChange}>✔</button>
				</div>
				:
				<>
					<button onClick={() => setEditingHistorySize(true)}>✎</button>
					<span> {historySize}</span>
				</>}
			<br />
			<label>
				<strong>Suggestions size:</strong>
			</label>
			<br />
			{editingSuggestionsSize ?
				<div id='suggestions-size-edit-container'>
					<input
						id='suggestions-size-edit-input'
						type='number'
						value={newSuggestionsSize}
						onChange={(e) => setNewSuggestionsSize(e.target.value)} />
					<button id='suggestions-size-edit-button' onClick={handleSuggestionsSizeChange}>✔</button>
				</div>
				:
				<>
					<button onClick={() => setEditingSuggestionsSize(true)}>✎</button>
					<span> {suggestionsSize}</span>
				</>}
			<br />
			<button onClick={recreateNgramTable}>Recreate ngram table</button>
			<br />
			<label>
				<strong>Sources: </strong>
				<button onClick={rescanSources}>Rescan</button>
			</label>
			<br />
			{loadingSources ?
				<span>Loading…</span>
				:
				<>
					<input
						type='text'
						placeholder='/path/to/new/source'
						value={newSource}
						onChange={(e) => setNewSource(e.target.value)}
						onKeyDown={(e) => {
							if (e.key === 'Enter') {
								addSource();
							}
						}} />
					<ul>
						{sources.map((source) => {
							return (
								<li
									key={source}
								>
									<button onClick={() => removeSource(source)}>✕</button>
									{source}
								</li>
							);
						})}
					</ul>
				</>}
		</>
	);
}
