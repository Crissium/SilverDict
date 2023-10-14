import React, { useEffect, useCallback } from 'react';
import { isRTL } from '../utils';

export function Suggestions(props) {
	const { suggestions, selectedSuggestionIndex, setSelectedSuggestionIndex, search } = props;

	const handleKeyDown = useCallback((e) => {
		if (e.key === 'ArrowDown') {
			e.preventDefault();
			if (selectedSuggestionIndex < 9) { // have to hard code this because suggestions are not fetched yet
				setSelectedSuggestionIndex(selectedSuggestionIndex + 1);
			}
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			if (selectedSuggestionIndex > 0) {
				setSelectedSuggestionIndex(selectedSuggestionIndex - 1);
			}
		}
	}, [selectedSuggestionIndex, setSelectedSuggestionIndex]);

	useEffect(function() {
		document.addEventListener('keydown', handleKeyDown);

		// Clean up the event listener when the component unmounts
		return () => {
			document.removeEventListener('keydown', handleKeyDown);
		};
	}, [handleKeyDown]);

	function getSuggestionClassName(length, index) {
		if (length === 0) {
			return '';
		} else if (index === selectedSuggestionIndex) {
			return 'clickable active';
		} else {
			return 'clickable';
		}
	}

	return (
		<div className='suggestions'>
			<ul>
				{suggestions.map((suggestion, index) => {
					return (
						<li
							key={index}
							style={{textAlign: isRTL(suggestion) ? 'right' : 'left'}}
							onClick={() => search(suggestion)}
							className={getSuggestionClassName(suggestion.length, index)}
						>
							{suggestion}
						</li>
					);
				})}
			</ul>
		</div>
	);
}
