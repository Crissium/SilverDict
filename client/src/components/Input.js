import React from 'react';

export function Input(props) {
	const { query, setQuery, handleEnterKeydown } = props;

	function handleQueryChange(e) {
		setQuery(e.target.value);
	}

	return (
		<input
			type='text'
			placeholder='Search…'
			value={query}
			onChange={handleQueryChange}
			onKeyDown={handleEnterKeydown} />
	);
}
