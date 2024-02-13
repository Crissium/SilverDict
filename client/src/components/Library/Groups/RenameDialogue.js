import React from 'react';
import FormDialogue from '../../common/FormDialogue';
import LoadingDialogue from '../../common/LoadingDialogue';
import { useAppContext } from '../../../AppContext';
import { API_PREFIX } from '../../../config';
import { JSON_HEADER, loadJson } from '../../../utils';
import { localisedStrings } from '../../../l10n';

export default function RenameDialogue(props) {
	const { opened, setOpened, handleClose, index } = props;
	const { groups, setGroups, setGroupings } = useAppContext();

	function handleSubmit(newName) {
		if (newName.length === 0) {
			handleClose();
			return;
		}

		fetch(`${API_PREFIX}/management/group_name`, {
			method: 'PUT',
			headers: JSON_HEADER,
			body: JSON.stringify({ old: groups[index].name, new: newName })
		})
			.then(loadJson)
			.then((data) => {
				setGroups(data['groups']);
				setGroupings(data['groupings']);
				handleClose();
			})
			.catch((error) => {
				alert(localisedStrings['failure-renaming-group'] + '\n' + error);
				handleClose();
			});
	}

	if (groups[index])
		return (
			<FormDialogue
				opened={opened}
				setOpened={setOpened}
				title={localisedStrings['library-screen-rename-group-dialogue-title']}
				content=''
				originalValue={groups[index].name}
				handleSubmittedData={handleSubmit}
				inputType='text'
				placeholder=''
				autoCapitalise='on'
			/>
		);
	else
		return (
			<LoadingDialogue
				opened={opened}
				setOpened={setOpened}
				title={localisedStrings['library-screen-rename-group-dialogue-title']}
			/>	
		);
}
