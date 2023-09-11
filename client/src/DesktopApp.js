import React, { useState, useEffect, useRef } from 'react';
import { API_PREFIX } from './config';
import { loadDataFromYamlResponse, convertDictionarySnakeCaseToCamelCase } from './utils';
import { Input } from './components/Input';
import { Suggestions } from './components/Suggestions';
import { History } from './components/History';
import { Article } from './components/Article';
import { Dictionaries } from './components/Dictionaries';
import { DictionaryManager } from './components/DictionaryManager';
import { Settings } from './components/Settings';
import { Dialogue } from './components/Dialogue';
import { GroupManager } from './components/GroupManager';

export default function DesktopApp() {
	const [query, setQuery] = useState('');

	const [history, setHistory] = useState([]);
	const [suggestions, setSuggestions] = useState([]);
	const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(0);

	const clickListener = useRef((event) => {});

	const [dictionaries, setDictionaries] = useState([]);
	const [groups, setGroups] = useState([]);
	const [groupings, setGroupings] = useState({});

	const [activeGroup, setActiveGroup] = useState('Default Group');

	const [article, setArticle] = useState('');

	const [dictionaryManagerOpened, setDictionaryManagerOpened] = useState(false);
	const [groupManagerOpened, setGroupManagerOpened] = useState(false);
	const [miscSettingsOpened, setMiscSettingsOpened] = useState(false);

	const [historySize, setHistorySize] = useState(100);

	useEffect(function () {
		fetch(`${API_PREFIX}/management/dictionaries`)
			.then(loadDataFromYamlResponse)
			.then((data) => {
				setDictionaries(data.map(convertDictionarySnakeCaseToCamelCase));
			});

		fetch(`${API_PREFIX}/management/groups`)
			.then(loadDataFromYamlResponse)
			.then((data) => {
				setGroups(data);
				setActiveGroup(data[0].name);
			});

		fetch(`${API_PREFIX}/management/dictionary_groupings`)
			.then(loadDataFromYamlResponse)
			.then((data) => {
				setGroupings(data);
			});

		fetch(`${API_PREFIX}/management/history`)
			.then(loadDataFromYamlResponse)
			.then((data) => {
				setHistory(data);
			});
	}, []);

	useEffect(function () {
		search(query);
		// Have to put it here because search() seems to form a closure which remembers the old value of activeGroup.
		// But we may be adding a countless number of click listeners here.
		document.removeEventListener('click', clickListener.current);
		clickListener.current = (event) => {
			if (event.target.matches('a')) {
				const href = event.target.getAttribute('href');
				if (href && href.startsWith('/api/lookup')) {
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
			setSuggestions(Array(10).fill(''));
		} else {
			fetch(`${API_PREFIX}/suggestions/${activeGroup}/${query}`)
				.then(loadDataFromYamlResponse)
				.then((data) => {
					setSuggestions(data);
				});
		}
	}, [activeGroup, query]);

	function search(newQuery) {
		if (newQuery.length === 0) {
			return;
		}

		newQuery = decodeURIComponent(newQuery);
		setQuery(newQuery);

		// Clean up previous scripts to avoid potential conflicts and DOM tree clutter
		const scripts = document.querySelectorAll('script');
		scripts.forEach((script) => {
			script.remove();
		});

		fetch(`${API_PREFIX}/query/${activeGroup}/${newQuery}`)
			.then(response => response.text()) // response here is HTML
			.then((html) => {
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
					.then(loadDataFromYamlResponse)
					.then((data) => {
						setHistory(data);
					});
			})
			.catch((error) => {
				alert('Failed to fetch articles.')
			});
	}

	function handleEnterKeydown(e) {
		if (e.key === 'Enter') {
			search(suggestions[selectedSuggestionIndex]);
			setSelectedSuggestionIndex(0);
		}
	}

	return (
		<div className='app-container'>
			<div className='left-pane'>
				<div className='query-area'>
					<Input
						query={query}
						setQuery={setQuery}
						handleEnterKeydown={handleEnterKeydown}
						isMobile={false}
					/>
					<Suggestions
						suggestions={suggestions}
						selectedSuggestionIndex={selectedSuggestionIndex}
						setSelectedSuggestionIndex={setSelectedSuggestionIndex}
						search={search}
					/>
				</div>
				<History
					showHeadingsAndButtons={true}
					history={history}
					setHistory={setHistory}
					historySize={historySize}
					search={search}
				/>
			</div>
			<Article article={article} />
			<div className='right-pane'>
				<div className='controls'>
					<Dialogue
						id='dialogue-dictionary-manager'
						icon='📖'
						opened={dictionaryManagerOpened}
						setOpened={setDictionaryManagerOpened}
					>
						<DictionaryManager
							dictionaries={dictionaries}
							setDictionaries={setDictionaries}
							groupings={groupings}
							setGroupings={setGroupings}
						/>
					</Dialogue>
					<Dialogue
						id='dialogue-group-manager'
						icon='📚'
						opened={groupManagerOpened}
						setOpened={setGroupManagerOpened}
					>
						<GroupManager
							dictionaries={dictionaries}
							setDictionaries={setDictionaries}
							groups={groups}
							setGroups={setGroups}
							groupings={groupings}
							setGroupings={setGroupings}
						/>
					</Dialogue>
					<Dialogue
						id='dialogue-settings'
						icon='⚙'
						opened={miscSettingsOpened}
						setOpened={setMiscSettingsOpened}
					>
						<Settings
							historySize={historySize}
							setHistorySize={setHistorySize}
							setHistory={setHistory}
							setDictionaries={setDictionaries}
							setGroupings={setGroupings}
						/>
					</Dialogue>
				</div>
				<Dictionaries
					dictionaries={dictionaries}
					groups={groups}
					groupings={groupings}
					activeGroup={activeGroup}
					setActiveGroup={setActiveGroup}
					isMobile={false}
				/>
			</div>
		</div>
	);
}
