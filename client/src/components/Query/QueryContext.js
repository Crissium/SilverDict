import React, { createContext, useCallback, useContext, useEffect, useRef, useState } from 'react';
import { API_PREFIX } from '../../config';
import { loadJson, getElementByName } from '../../utils';
import { useAppContext } from '../../AppContext';
import { localisedStrings } from '../../l10n';

const QueryContext = createContext();

export function QueryProvider({ children }) {
	const { dictionaries, groups, groupings, setHistory, sizeSuggestion } = useAppContext();

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
	const queryContentRef = useRef(null);

	const [initialQueryProcessed, setInitialQueryProcessed] = useState(false);

	function setShowingArticleView(isShowing, isScrollToTop) {
		setShowingArticle(isShowing);
		if (isScrollToTop) {
			if (queryContentRef.current) {
				queryContentRef.current.scrollIntoView();
			} else if (articleViewRef.current) {
				articleViewRef.current.scrollIntoView();
			}
		}
	}

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

	const search = useCallback(function (newSearch, articleName) {
		if (newSearch.length === 0) {
			return;
		}

		// Note: I actually have forgotten why I have to decode it first... Stupid me, didn't put a word of comment here
		try {
			newSearch = decodeURIComponent(newSearch);
			newSearch = encodeURIComponent(newSearch);
		}
		catch (error) {
			newSearch = encodeURIComponent(newSearch);
		}

		fetch(`${API_PREFIX}/query/${nameActiveGroup}/${newSearch}?dicts=true`)
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
				fetch(`${API_PREFIX}/management/history`)
					.then(loadJson)
					.then((data) => {
						setHistory(data);
					});
			})
			.then(() => {
				if (articleName) {
					async function scrollToArticle() {
						const element = await getElementByName(articleName);
						if (element) {
							element.scrollIntoView({ block: 'center' });
						}
					}
					scrollToArticle();
				}
			})
			.catch((error) => {
				resetNamesActiveDictionaries();
				alert(localisedStrings['failure-fetching-articles'] + '\n' + error);
			});
	}, [nameActiveGroup]);

	const clickListener = useCallback(function (event) {
		if (event.target.matches('a')) {
			const href = event.target.getAttribute('href');
			if (href && href.startsWith(`${API_PREFIX}/query`)) {
				event.preventDefault();
				const [newSearchTerm, articleName] = href.split('/').pop().split('#');
				search(newSearchTerm, articleName);
				setShowingArticleView(true, true);
			}
		}
	}, [search]);

	useEffect(function () {
		document.addEventListener('click', clickListener);
		
		return function () {
			document.removeEventListener('click', clickListener);
		};
	}, [clickListener]);

	useEffect(function () {
		search(searchTerm);
		if (article.length !== 0) {
			setShowingArticleView(true, true);
		}
	}, [search]);

	useEffect(function() {
		// Handle URLs with parameters like /?group=English&key=hello
		if (groups && groups.length > 0 && !initialQueryProcessed) {
			const queryParams = new URLSearchParams(window.location.search);
	
			let groupIsDefault = true;
			const requestedGroup = queryParams.get('group');
			if (requestedGroup && requestedGroup != nameActiveGroup) {
				groups.map((group) => {
					if (group.name === requestedGroup) {
						setNameActiveGroup(requestedGroup);
						groupIsDefault = false;
					}
				});
			}
			
			const key = queryParams.get('key');
			if (key) {
				setSearchTerm(key);
				if (groupIsDefault) { // Otherwise search is triggered because the active group has changed
					search(key);
				}
				setShowingArticleView(true, true);
			}

			setInitialQueryProcessed(true);
		}
	}, [groups, initialQueryProcessed]);

	return (
		<QueryContext.Provider
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
				setShowingArticleView,
				queryContentRef,
				search
			}}
		>
			{children}
		</QueryContext.Provider>
	);
}

export function useQueryContext() {
	return useContext(QueryContext);
}
