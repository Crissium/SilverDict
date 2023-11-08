import React, { useState, useEffect, useRef } from 'react';
import { API_PREFIX } from './config';
import { loadDataFromJsonResponse, convertDictionarySnakeCaseToCamelCase } from './utils';
import { Input } from './components/Input';
import { Suggestions } from './components/Suggestions';
import { History } from './components/History';
import { Article } from './components/Article';
import { Dictionaries } from './components/Dictionaries';
import { Dialogue } from './components/Dialogue';

export default function MobileApp() {
	const [query, setQuery] = useState('');

	const [history, setHistory] = useState([]);
	const [historySize, setHistorySize] = useState(100);

	const [latestSuggestionsTimestamp, setLatestSuggestionsTimestamp] = useState(0);
	const [suggestions, setSuggestions] = useState([]);
	const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(0);

	const clickListener = useRef((event) => { });

	const [dictionaries, setDictionaries] = useState([]);
	const [groups, setGroups] = useState([]);
	const [groupings, setGroupings] = useState({});

	const [activeGroup, setActiveGroup] = useState('Default Group');

	const [article, setArticle] = useState('');

	const [dictionariesHavingQuery, setDictionariesHavingQuery] = useState([]);

	const [dictionariesOpened, setDictionariesOpened] = useState(false);

	const [suggestionsSize, setSuggestionsSize] = useState(10);

	useEffect(function () {
		fetch(`${API_PREFIX}/management/dictionaries`)
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setDictionaries(data.map(convertDictionarySnakeCaseToCamelCase));
			});

		fetch(`${API_PREFIX}/management/groups`)
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setGroups(data);
				setActiveGroup(data[0].name);
			});

		fetch(`${API_PREFIX}/management/dictionary_groupings`)
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setGroupings(data);
			});

		fetch(`${API_PREFIX}/management/history`)
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setHistory(data);
			});

		fetch(`${API_PREFIX}/management/history_size`)
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setHistorySize(data['size']);
			});

		fetch(`${API_PREFIX}/management/num_suggestions`)
			.then(loadDataFromJsonResponse)
			.then((data) => {
				setSuggestionsSize(data['size']);
			});
	}, []);

	function resetDictionariesHavingQuery() {
		if (groupings[activeGroup]) {
			const dictionariesInGroup = [];
			for (let dictionary of dictionaries) {
				if (groupings[activeGroup].includes(dictionary.name)) {
					dictionariesInGroup.push(dictionary.name);
				}
			}
			setDictionariesHavingQuery(dictionariesInGroup);
		}
	}

	useEffect(function () {
		search(query);
		document.removeEventListener('click', clickListener.current);
		clickListener.current = (event) => {
			if (event.target.matches('a')) {
				const href = event.target.getAttribute('href');
				if (href && href.startsWith('/api/query')) {
					event.preventDefault();
					const query = href.split('/').pop().split('#')[0];
					search(query);
				}
			}
		};
		document.addEventListener('click', clickListener.current);
	}, [activeGroup]);

	useEffect(function () {
		if (query.length === 0) {
			setLatestSuggestionsTimestamp(Date.now());
			setSuggestions(['']);
			resetDictionariesHavingQuery();
		} else {
			fetch(`${API_PREFIX}/suggestions/${activeGroup}/${encodeURIComponent(query)}?timestamp=${Date.now()}`)
				.then(loadDataFromJsonResponse)
				.then((data) => {
					if (data['timestamp'] > latestSuggestionsTimestamp) {
						setLatestSuggestionsTimestamp(data['timestamp']);
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
					alert('Failed to fetch suggestions.');
				});
		}
	}, [dictionaries, groupings, activeGroup, query, suggestionsSize]);

	function search(newQuery) {
		if (newQuery.length === 0) {
			return;
		}

		try {
			newQuery = decodeURIComponent(newQuery);
			// setQuery(newQuery);
			newQuery = encodeURIComponent(newQuery);
		}
		catch (error) {
			// setQuery(newQuery);
			newQuery = encodeURIComponent(newQuery);
		}

		// Clean up previous scripts to avoid potential conflicts and DOM tree clutter
		const scripts = document.querySelectorAll('script');
		scripts.forEach((script) => {
			script.remove();
		});

		fetch(`${API_PREFIX}/query/${activeGroup}/${newQuery}?dicts=True`)
			.then(loadDataFromJsonResponse)
			.then((data) => {
				const html = data['articles'];
				setDictionariesHavingQuery(data['dictionaries']);
				// Fix an error where the dynamically loaded script is not executed
				const scriptSrcMatches = [...html.matchAll(/<script.*?src=["'](.*?)["']/gi)];
				const scriptSrcs = scriptSrcMatches.map((match) => match[1]);
				if (scriptSrcs.length !== 0) {
					scriptSrcs.forEach((src) => {
						const script = document.createElement('script');
						script.src = src;
						document.body.appendChild(script);
					})
				}
				return html;
			})
			.then((html) => {
				setArticle(html);
				// Nesting this inside then() to ensure history is fetched after the query has been processed by the server
				fetch(`${API_PREFIX}/management/history`)
					.then(loadDataFromJsonResponse)
					.then((data) => {
						setHistory(data);
					});
			})
			.catch((error) => {
				resetDictionariesHavingQuery();
				alert('Failed to fetch articles.')
			})
			.finally(() => {
				if (article.length > 0) {
					document.getElementsByClassName('article')[0].focus();
				}
			});
	}

	function handleEnterKeydown(e) {
		if (e.key === 'Enter') {
			search(suggestions[selectedSuggestionIndex]);
			setSelectedSuggestionIndex(0);
			document.querySelector('input').blur();
		}
	}

	function handleGoBack() {
		const lastQuery = history[1];
		if (lastQuery) {
			search(lastQuery);
		}
	}

	return (
		<div className='app-container'>
			<div className='input-container'>
				<Input
					query={query}
					setQuery={setQuery}
					handleEnterKeydown={handleEnterKeydown}
					isMobile={true}
					setArticle={setArticle}
				/>
				<Dialogue
					id='dialogue-dictionaries'
					icon='📚'
					opened={dictionariesOpened}
					setOpened={setDictionariesOpened}
				>
					<Dictionaries
						dictionaries={dictionaries}
						groups={groups}
						groupings={groupings}
						activeGroup={activeGroup}
						setActiveGroup={setActiveGroup}
						dictionariesHavingQuery={dictionariesHavingQuery}
						isMobile={true}
						historySize={historySize}
						setHistorySize={setHistorySize}
						setHistory={setHistory}
						setDictionaries={setDictionaries}
						setGroups={setGroups}
						setGroupings={setGroupings}
						suggestionsSize={suggestionsSize}
						setSuggestionsSize={setSuggestionsSize}
						setDictionariesOpened={setDictionariesOpened}
					/>
				</Dialogue>
			</div>
			{article.length === 0 ? (
				query.length === 0 ? (
					<History
						showHeadingsAndButtons={false}
						history={history}
						setHistory={setHistory}
						historySize={historySize}
						search={search}
					/>
				) : (
					<Suggestions
						suggestions={suggestions}
						selectedSuggestionIndex={selectedSuggestionIndex}
						setSelectedSuggestionIndex={setSelectedSuggestionIndex}
						search={search}
					/>
				)
			) : (
				<Article
					article={article}
					setQuery={setQuery}
					isMobile={true}
					handleGoBack={handleGoBack}
				/>
			)}
		</div>
	);
}