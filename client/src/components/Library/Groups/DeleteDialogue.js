import React from 'react';
import ConfirmationDialogue from '../../common/ConfirmationDialogue';
import LoadingDialogue from '../../common/LoadingDialogue';
import { useAppContext } from '../../../AppContext';
import { API_PREFIX } from '../../../config';
import { JSON_HEADER, loadJson } from '../../../utils';
import { localisedStrings } from '../../../l10n';

export default function DeleteDialogue(props) {
	const { opened, setOpened, handleClose, index } = props;
	const { groups, setGroups, setGroupings } = useAppContext();

	function handleConfirm() {
		fetch(`${API_PREFIX}/management/groups`, {
			method: 'DELETE',
			headers: JSON_HEADER,
			body: JSON.stringify({ name: groups[index].name })
		})
			.then(loadJson)
			.then((data) => {
				setGroups(data['groups']);
				setGroupings(data['groupings']);
				handleClose();
			})
			.catch((error) => {
				alert(localisedStrings['failure-deleting-group'] + '\n' + error);
				handleClose();
			});
	}

	if (groups[index])
		return (
			<ConfirmationDialogue
				opened={opened}
				setOpened={setOpened}
				title={localisedStrings['library-screen-delete-group-dialogue-title']}
				content={localisedStrings.formatString(
					localisedStrings['library-screen-delete-group-dialogue-confirmation'],
					groups[index].name
				)}
				onConfirm={handleConfirm}
			/>
		);
	else
		return (
			<LoadingDialogue
				opened={opened}
				setOpened={setOpened}
				title={localisedStrings['library-screen-delete-group-dialogue-title']}
			/>
		);
}
