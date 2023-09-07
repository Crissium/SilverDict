import React from 'react';

export function Dictionaries(props) {
	const { dictionaries, groups, groupings, activeGroup, setActiveGroup } = props;

	function navigateToDictionary(name) {
		const link = document.createElement('a');
		link.href = `#${name}`;
		link.click();
	}

	if (groupings[activeGroup])
		return (
			<div className='dictionaries'>
				<select
					className='heading'
					value={activeGroup}
					onChange={(e) => setActiveGroup(e.target.value)}
				>
					{groups.map((group) => {
						return (
							<option
								key={group.name}
								value={group.name}
							>
								{group.name}
							</option>
						);
					})}
				</select>

				<ul>
					{dictionaries.map((dictionary) => {
						if (groupings[activeGroup].has(dictionary.name)) {
							return (
								<li
									key={dictionary.name}
									className='clickable'
									onClick={() => navigateToDictionary(dictionary.name)}
								>
									{dictionary.displayName}
								</li>
							);
						} else {
							return null;
						}
					})}
				</ul>
			</div>
		);
}
