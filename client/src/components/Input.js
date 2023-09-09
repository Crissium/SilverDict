import React, { useEffect } from 'react';

export function Input(props) {
	const { query, setQuery, handleEnterKeydown, isMobile, setArticle } = props;

	useEffect(function() {
		// Give input focus on window load
		window.onload = () => {
			document.querySelector('input').focus();
		};
	}, []);

	function handleQueryChange(e) {
		setQuery(e.target.value);
	}

	if (isMobile)
		return (
			<input
				type='text'
				placeholder='Search…'
				value={query}
				onFocus={() => setArticle('')}
				onChange={handleQueryChange}
				onKeyDown={handleEnterKeydown}
			/>
		);
	else
		return (
			<input
				type='text'
				placeholder='Search…'
				value={query}
				onChange={handleQueryChange}
				onKeyDown={handleEnterKeydown}
			/>
		);
}
