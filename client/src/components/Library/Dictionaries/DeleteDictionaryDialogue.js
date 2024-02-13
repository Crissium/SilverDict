import React from 'react';
import ConfirmationDialogue from '../../common/ConfirmationDialogue';
import LoadingDialogue from '../../common/LoadingDialogue';
import { useAppContext } from '../../../AppContext';
import { API_PREFIX } from '../../../config';
import { JSON_HEADER, loadJson, dictionarySnake2Camel } from '../../../utils';
import { localisedStrings } from '../../../l10n';

export default function DeleteDictionaryDialogue(props) {
	const { opened, setOpened, handleClose, index } = props;
	const { dictionaries, setDictionaries, setGroupings } = useAppContext();

	function handleConfirm() {
		fetch(`${API_PREFIX}/management/dictionaries`, {
			method: 'DELETE',
			headers: JSON_HEADER,
			body: JSON.stringify({ name: dictionaries[index].name })
		})
			.then(loadJson)
			.then((data) => {
				setDictionaries(data['dictionaries'].map(dictionarySnake2Camel));
				setGroupings(data['groupings']);
				handleClose();
			})
			.catch((error) => {
				alert(localisedStrings['failure-deleting-dictionary'] + '\n' + error);
				handleClose();
			});
	}

	if (dictionaries[index])
		return (
			<ConfirmationDialogue
				opened={opened}
				setOpened={setOpened}
				title={localisedStrings['library-screen-delete-dictionary-dialogue-title']}
				content={localisedStrings.formatString(
					localisedStrings['library-screen-delete-dictionary-dialogue-confirmation'],
					dictionaries[index].displayName
				)}
				onConfirm={handleConfirm}
			/>
		);
	else
		return (
			<LoadingDialogue
				opened={opened}
				setOpened={setOpened}
				title={localisedStrings['library-screen-delete-dictionary-dialogue-title']}
			/>
		);
}
