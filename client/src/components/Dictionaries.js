import React, { useState } from 'react';
import { Dialogue } from './Dialogue';
import { DictionaryManager } from './DictionaryManager';
import { GroupManager } from './GroupManager';
import { Settings } from './Settings';

export function Dictionaries(props) {
	const { dictionaries, groups, groupings, activeGroup, setActiveGroup, dictionariesHavingQuery, isMobile, historySize, setHistorySize, setHistory, setDictionaries, setGroups, setGroupings, suggestionsSize, setSuggestionsSize, setDictionariesOpened } = props;

	// The following three are used in the mobile interface only
	const [dictionaryManagerOpened, setDictionaryManagerOpened] = useState(false);
	const [groupManagerOpened, setGroupManagerOpened] = useState(false);
	const [miscSettingsOpened, setMiscSettingsOpened] = useState(false);

	function navigateToDictionary(name) {
		document.getElementById(name).scrollIntoView();
		if (isMobile)
			setDictionariesOpened(false);
	}

	if (groupings[activeGroup] && dictionariesHavingQuery)
		return (
			<>
				{isMobile && (
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
								suggestionsSize={suggestionsSize}
								setSuggestionsSize={setSuggestionsSize}
							/>
						</Dialogue>
					</div>
				)}
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
							if (groupings[activeGroup].includes(dictionary.name) && dictionariesHavingQuery.includes(dictionary.name)) {
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
			</>
		);
}
