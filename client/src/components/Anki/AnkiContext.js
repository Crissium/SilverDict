import React, { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { API_PREFIX } from '../../config';
import { loadJson } from '../../utils';
import { useAppContext } from '../../AppContext';
import { localisedStrings } from '../../l10n';

const AnkiContext = createContext();

export function AnkiProvider({ children }) {
	const { dictionaries, groups, groupings, sizeSuggestion } = useAppContext();

	const [searchTerm, setSearchTerm] = useState('');

	const inputRef = useRef(null);

	const [suggestionTimestamp, setSuggestionTimestamp] = useState(0);
	const [suggestions, setSuggestions] = useState([]);

	const [nameActiveGroup, setNameActiveGroup] = useState('Default Group');
	const [namesActiveDictionaries, setNamesActiveDictionaries] = useState([]);

	const [article, setArticle] = useState('');
	
	const articleViewRef = useRef(null);

	// On mobile only
	const [dictionariesDialogueOpened, setDictionariesDialogueOpened] = useState(false);
	const [showingArticle, setShowingArticle] = useState(false);
	const ankiContentRef = useRef(null);

	useEffect(function () {
		setNameActiveGroup('Default Group');
	}, [groups.length]);

	function resetNamesActiveDictionaries() {
		if (groupings[nameActiveGroup]) {
			const dictionariesInGroup = [];
			for (let dictionary of dictionaries) {
				if (groupings[nameActiveGroup].includes(dictionary.name)) {
					dictionariesInGroup.push(dictionary.name);
				}
			}
			setNamesActiveDictionaries(dictionariesInGroup);
		}
	}

	useEffect(function () {
		if (searchTerm.length === 0) {
			setSuggestionTimestamp(Date.now());
			setSuggestions(['']);
			resetNamesActiveDictionaries();
		} else {
			fetch(`${API_PREFIX}/suggestions/${nameActiveGroup}/${encodeURIComponent(searchTerm)}?timestamp=${Date.now()}`)
				.then(loadJson)
				.then((data) => {
					if (data['timestamp'] > suggestionTimestamp) {
						setSuggestionTimestamp(data['timestamp']);
						// Filter out empty suggestions
						const newSuggestions = data['suggestions'].filter((suggestion) => suggestion.length > 0);
						if (newSuggestions.length > 0) {
							setSuggestions(newSuggestions);
						} else {
							setSuggestions(['']);
						}
					}
				})
				.catch((error) => {
					alert(localisedStrings['failure-fetching-suggestions'] + '\n' + error);
				});
		}
	}, [dictionaries, groupings, nameActiveGroup, searchTerm, sizeSuggestion]);

	const search = useCallback(function (newSearch) {
		if (newSearch.length === 0) {
			return;
		}

		try {
			newSearch = decodeURIComponent(newSearch);
			newSearch = encodeURIComponent(newSearch);
		}
		catch (error) {
			newSearch = encodeURIComponent(newSearch);
		}

		fetch(`${API_PREFIX}/anki/${nameActiveGroup}/${newSearch}?dicts=true`)
			.then(loadJson)
			.then((data) => {
				const html = data['articles'];
				setNamesActiveDictionaries(data['dictionaries']);

				// Fix an error where the dynamically loaded script is not executed
				const scriptSrcMatches = [...html.matchAll(/<script.*?src=["'](.*?)["']/gi)];
				const scriptSrcs = scriptSrcMatches.map((match) => match[1]);
				if (scriptSrcs.length !== 0) {
					scriptSrcs.forEach((src) => {
						const script = document.createElement('script');
						script.src = src;
						document.body.appendChild(script);
					});
				}
				return html;
			})
			.then((html) => {
				setArticle(html);
			})
			.then(() => {
				// Scroll to top of article
				if (articleViewRef.current) {
					// On the mobile interface, this will fail because the view hasn't been mounted yet
					articleViewRef.current.scrollIntoView({ block: 'start' });
				}
			})
			.catch((error) => {
				resetNamesActiveDictionaries();
				alert(localisedStrings['failure-fetching-articles'] + '\n' + error);
			});
	}, [nameActiveGroup]);

	useEffect(function () {
		search(searchTerm);
		if (article.length !== 0) {
			setShowingArticle(true);
		}
	}, [search]);

	return (
		<AnkiContext.Provider
			value={{
				searchTerm,
				setSearchTerm,
				inputRef,
				suggestions,
				article,
				setArticle,
				articleViewRef,
				nameActiveGroup,
				setNameActiveGroup,
				namesActiveDictionaries,
				setNamesActiveDictionaries,
				dictionariesDialogueOpened,
				setDictionariesDialogueOpened,
				showingArticle,
				setShowingArticle,
				ankiContentRef,
				search
			}}
		>
			{children}
		</AnkiContext.Provider>
	);
}

export function useAnkiContext() {
	return useContext(AnkiContext);
}
