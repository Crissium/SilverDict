import React from 'react';

export function Input(props) {
	const { query, setQuery, handleEnterKeydown, isMobile, setArticle } = props;

	function handleQueryChange(e) {
		setQuery(e.target.value);
	}

	function handleMobileInputFocus(e) {
		e.target.select();
		setArticle('');
	}

	if (isMobile)
		return (
			<input
				type='text'
				placeholder='Search…'
				value={query}
				autoFocus={true}
				autoCapitalize='off'
				onFocus={handleMobileInputFocus}
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
				autoFocus={true}
				onChange={handleQueryChange}
				onKeyDown={handleEnterKeydown}
			/>
		);
}
