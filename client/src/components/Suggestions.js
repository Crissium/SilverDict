import React, { useState, useEffect } from 'react';
import { API_PREFIX } from '../config';
import { loadDataFromYamlResponse } from '../utils';

export function Suggestions(props) {
	const { activeGroup, query, search } = props;
	const [suggestions, setSuggestions] = useState([]);

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

	return (
		<div className='suggestions'>
			<ul>
				{suggestions.map((suggestion, index) => {
					return (
						<li
							key={index}
							onClick={() => search(suggestion)}
							className={suggestion.length !== 0 ? 'clickable' : ''}
						>
							{suggestion}
						</li>
					);
				})}
			</ul>
		</div>
	);
}
