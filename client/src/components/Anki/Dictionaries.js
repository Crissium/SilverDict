import React, { useState } from 'react';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Snackbar from '@mui/material/Snackbar';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import { useAppContext } from '../../AppContext';
import { useAnkiContext } from './AnkiContext';
import { isRTL } from '../../utils';
import { localisedStrings } from '../../l10n';

function DictionaryListItem(props) {
	const { name, displayName } = props;
	const { setDictionariesDialogueOpened } = useAnkiContext();
	const [messageOpened, setMessageOpened] = useState(false);

	function navigateToDictAndCopy(name) {
		setDictionariesDialogueOpened(false);
		const dict = document.getElementById(name);
		if (dict) {
			dict.scrollIntoView();
			
			navigator.clipboard.writeText(dict.innerHTML)
				.then(() => {
					setMessageOpened(true);
				})
				.catch((error) => {
					alert(localisedStrings['anki-failure-copying'] + '\n' + error);
				});
		}
	}

	return (
		<>
			<ListItem key={name}>
				<ListItemButton onClick={() => navigateToDictAndCopy(name)}>
					<ListItemText
						primary={displayName}
						primaryTypographyProps={{
							dir: isRTL(displayName) ? 'rtl' : 'ltr'
						}}
					/>
				</ListItemButton>
			</ListItem>
			<Snackbar
				open={messageOpened}
				onClose={(e, reason) => setMessageOpened(false)}
				autoHideDuration={2000}
				message={localisedStrings['anki-dictionary-content-copied-message']}
			/>
		</>
	);
}

export default function Dictionaries() {
	const { dictionaries, groups, groupings } = useAppContext();
	const { nameActiveGroup, setNameActiveGroup, namesActiveDictionaries, setDictionariesDialogueOpened } = useAnkiContext();

	function handleGroupChange(e) {
		setNameActiveGroup(e.target.value);
		setDictionariesDialogueOpened(false);
	}

	if (groupings && groupings[nameActiveGroup] && namesActiveDictionaries)
		return (
			<>
				<FormControl
					fullWidth
					style={{flexShrink: 0, flexGrow: 0}}
				>
					<Select
						value={nameActiveGroup}
						onChange={handleGroupChange}
					>
						{groups.map((group) => {
							return (
								<MenuItem
									key={group.name}
									value={group.name}
								>
									{group.name}
								</MenuItem>
							);
						})}
					</Select>
				</FormControl>
				<List
					style={{flexShrink: 1, flexGrow: 1, overflow: 'auto'}}
				>
					{dictionaries.map((dict) => {
						if (groupings[nameActiveGroup].includes(dict.name) &&
							namesActiveDictionaries.includes(dict.name))
							return (
								<DictionaryListItem
									name={dict.name}
									displayName={dict.displayName}
								/>
							);
						else
							return null;
					})}
				</List>
			</>
		);
	else
		return (
			<List>
				{dictionaries.map((dict) => (
					<DictionaryListItem
						name={dict.name}
						displayName={dict.displayName}
					/>
				))}
			</List>
		);
}
