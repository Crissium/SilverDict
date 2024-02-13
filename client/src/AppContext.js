import React, { createContext, useContext, useEffect, useState } from 'react';
import { API_PREFIX } from './config';
import { dictionarySnake2Camel, loadJson } from './utils';
import { localisedStrings } from './l10n';

const AppContext = createContext();

export function AppProvider({ children }) {
	const [dictionaries, setDictionaries] = useState([]);
	const [groups, setGroups] = useState([]);
	const [groupings, setGroupings] = useState({});

	const [history, setHistory] = useState([]);

	const [sizeSuggestion, setSizeSuggestion] = useState(10);
	const [sizeHistory, setSizeHistory] = useState(100);

	const [formats, setFormats] = useState([]);
	const [sources, setSources] = useState([]);

	const [drawerOpened, setDrawerOpened] = useState(false);

	async function initialise(
		setDictionaries,
		setGroups,
		setGroupings,
		setHistory,
		setSizeHistory,
		setSizeSuggestion,
		setFormats,
		setSources
	) {
		try {
			const [
				dictionariesData,
				groupsData,
				groupingsData,
				historyData,
				sizeHistoryData,
				sizeSuggestionData,
				formatsData,
				sourcesData
			] = await Promise.all([
				fetch(`${API_PREFIX}/management/dictionaries`).then(loadJson),
				fetch(`${API_PREFIX}/management/groups`).then(loadJson),
				fetch(`${API_PREFIX}/management/dictionary_groupings`).then(loadJson),
				fetch(`${API_PREFIX}/management/history`).then(loadJson),
				fetch(`${API_PREFIX}/management/history_size`).then(loadJson),
				fetch(`${API_PREFIX}/management/num_suggestions`).then(loadJson),
				fetch(`${API_PREFIX}/management/formats`).then(loadJson),
				fetch(`${API_PREFIX}/management/sources`).then(loadJson)
			]);

			setDictionaries(dictionariesData.map(dictionarySnake2Camel));
			setGroups(groupsData);
			setGroupings(groupingsData);
			setHistory(historyData);
			setSizeHistory(sizeHistoryData['size']);
			setSizeSuggestion(sizeSuggestionData['size']);
			setFormats(formatsData);
			setSources(sourcesData);
		} catch (error) {
			alert(localisedStrings['app-context-message-failure-initialising'] + '\n' + error);
		}
	}

	useEffect(function () {
		initialise(
			setDictionaries,
			setGroups,
			setGroupings,
			setHistory,
			setSizeHistory,
			setSizeSuggestion,
			setFormats,
			setSources
		);
	}, []);

	return (
		<AppContext.Provider
			value={{
				dictionaries,
				setDictionaries,
				groups,
				setGroups,
				groupings,
				setGroupings,
				history,
				setHistory,
				sizeHistory,
				setSizeHistory,
				sizeSuggestion,
				setSizeSuggestion,
				formats,
				setFormats,
				sources,
				setSources,
				drawerOpened,
				setDrawerOpened,
				initialise
			}}
		>
			{children}
		</AppContext.Provider>
	);
}

export function useAppContext() {
	return useContext(AppContext);
}
