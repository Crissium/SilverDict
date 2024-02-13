import React from 'react';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogActions from '@mui/material/DialogActions';
import DialogContent from '@mui/material/DialogContent';
import DialogTitle from '@mui/material/DialogTitle';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Checkbox from '@mui/material/Checkbox';
import LoadingDialogue from '../../common/LoadingDialogue';
import { API_PREFIX } from '../../../config';
import { useAppContext } from '../../../AppContext';
import { JSON_HEADER, loadJson, isRTL } from '../../../utils';
import { localisedStrings } from '../../../l10n';

function Item(props) {
	const { dictName, displayName, groupName, alreadyIncluded } = props;
	const { setGroupings } = useAppContext();

	function handleToggle() {
		const requestMethod = alreadyIncluded ? 'DELETE' : 'POST';

		fetch(`${API_PREFIX}/management/dictionary_groupings`, {
			method: requestMethod,
			headers: JSON_HEADER,
			body: JSON.stringify({ dictionary_name: dictName, group_name: groupName })
		})
			.then(loadJson)
			.then((data) => {
				setGroupings(data);
			})
			.catch((error) => {
				if (alreadyIncluded) {
					alert(localisedStrings['failure-removing-dictionary-from-group'] + '\n' + error);
				} else {
					alert(localisedStrings['failure-adding-dictionary-to-group'] + '\n' + error);
				}
			});
	}

	return (
		<ListItem
			disablePadding
			key={dictName}
		>
			<ListItemButton
				dense
				onClick={handleToggle}
			>
				<ListItemIcon>
					<Checkbox
						edge='start'
						checked={alreadyIncluded}
						tabIndex={-1}
						disableRipple
					/>
				</ListItemIcon>
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

export default function EditDictionariesDialogue(props) {
	const { opened, setOpened, handleClose, index } = props;
	const { dictionaries, groups, groupings } = useAppContext();

	function isIncluded(d) {
		return groupings[groups[index].name].includes(d.name);
	}

	if (dictionaries && groups[index])
		return (
			<Dialog
				maxWidth
				open={opened}
				onClose={(event, reason) => handleClose()}
			>
				<DialogTitle>
					{localisedStrings['library-screen-groups-table-actions-edit-dictionaries']}
				</DialogTitle>
				<DialogContent>
					<List>
						{dictionaries.map((d) => (
							<Item
								dictName={d.name}
								displayName={d.displayName}
								groupName={groups[index].name}
								alreadyIncluded={isIncluded(d)}
							/>
						))}
					</List>
				</DialogContent>
				<DialogActions>
					<Button
						onClick={handleClose}
					>
						{localisedStrings['generic-ok']}
					</Button>
				</DialogActions>
			</Dialog>
		);
	else
		return (
			<LoadingDialogue
				opened={opened}
				setOpened={setOpened}
				title={localisedStrings['library-screen-groups-table-actions-edit-dictionaries']}
			/>
		);
}
