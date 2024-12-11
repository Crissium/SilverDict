import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import { API_PREFIX } from '../../config';
import { loadJson } from '../../utils';
import { localisedStrings } from '../../l10n';

const FtsContext = createContext();

export function FtsProvider({ children }) {
	const [searchTerm, setSearchTerm] = useState('');

	const nameActiveGroup = 'Xapian'; // Hard coded yes, but this makes copy-pasting code easier
	const [articlesFound, setArticlesFound] = useState([]);

	const [article, setArticle] = useState('');

	const articleViewRef = useRef(null);

	// On mobile only
	const [articlesDialogueOpened, setArticlesDialogueOpened] = useState(false);
	const queryContentRef = useRef(null);

	function scrollToTop() {
		if (queryContentRef.current) {
			queryContentRef.current.scrollIntoView();
		} else if (articleViewRef.current) {
			articleViewRef.current.scrollIntoView();
		}
	}

	useEffect(function () {
		function listener(e) {
			if (e.target.matches('a')) {
				const href = e.target.getAttribute('href');
				if (href && href.startsWith(`${API_PREFIX}/query`)) {
					e.preventDefault();
					const [newSearchTerm, articleName] = href.split('/').pop().split('#');
					// Searching for the search term in a new tab
					window.open(`?group=${nameActiveGroup}&key=${newSearchTerm}`, '_blank');
				}
			}
		}
		document.addEventListener('click', listener);
		return () => document.removeEventListener('click', listener);
	}, []);

	function search(newSearch) {
		if (newSearch.length === 0) {
			return;
		}

		newSearch = encodeURIComponent(newSearch);

		fetch(`${API_PREFIX}/fts/${newSearch}?dicts=true`)
			.then(loadJson)
			.then((data) => {
				const html = data['articles'];
				setArticlesFound(data['dictionaries']);

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
			.catch((error) => {
				setArticlesFound([]);
				alert(localisedStrings['failure-fetching-articles'] + '\n' + error);
			});
	}

	return (
		<FtsContext.Provider
			value={{
				searchTerm,
				setSearchTerm,
				article,
				setArticle,
				articleViewRef,
				nameActiveGroup,
				articlesFound,
				setArticlesFound,
				articlesDialogueOpened,
				setArticlesDialogueOpened,
				queryContentRef,
				scrollToTop,
				search
			}}
		>
			{children}
		</FtsContext.Provider>
	);
}

export function useFtsContext() {
	return useContext(FtsContext);
}
