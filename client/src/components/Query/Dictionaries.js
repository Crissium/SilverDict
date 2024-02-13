import React from 'react';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import { useAppContext } from '../../AppContext';
import { useQueryContext } from './QueryContext';
import { isRTL } from '../../utils';

function DictionaryListItem(props) {
	const { name, displayName } = props;
	const { setDictionariesDialogueOpened } = useQueryContext();

	function navigateToDict(name) {
		setDictionariesDialogueOpened(false);
		const dict = document.getElementById(name);
		if (dict) {
			dict.scrollIntoView();
		}
	}

	return (
		<ListItem key={name}>
			<ListItemButton onClick={() => navigateToDict(name)}>
				<ListItemText
					primary={displayName}
					primaryTypographyProps={{
						dir: isRTL(displayName) ? 'rtl' : 'ltr'
					}}
				/>
			</ListItemButton>
		</ListItem>
	);
}

export default function Dictionaries() {
	const { dictionaries, groups, groupings } = useAppContext();
	const { nameActiveGroup, setNameActiveGroup, namesActiveDictionaries, setDictionariesDialogueOpened } = useQueryContext();

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
