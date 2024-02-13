import React from 'react';
import FormDialogue from '../../common/FormDialogue';
import LoadingDialogue from '../../common/LoadingDialogue';
import { useAppContext } from '../../../AppContext';
import { API_PREFIX } from '../../../config';
import { JSON_HEADER, loadJson } from '../../../utils';
import { localisedStrings } from '../../../l10n';

export default function RenameDictionaryDialogue(props) {
	const { opened, setOpened, handleClose, index } = props;
	const { dictionaries, setDictionaries } = useAppContext();

	function handleSubmit(newDisplayName) {
		if (newDisplayName.length === 0) {
			handleClose();
			return;
		}

		fetch(`${API_PREFIX}/management/dictionary_name`, {
			method: 'PUT',
			headers: JSON_HEADER,
			body: JSON.stringify({ name: dictionaries[index].name, display: newDisplayName })
		})
			.then(loadJson)
			.then((data) => {
				if (data.success) {
					const newDictionaries = [...dictionaries];
					newDictionaries[index].displayName = newDisplayName;
					setDictionaries(newDictionaries);
					handleClose();
				} else {
					alert(localisedStrings['failure-renaming-dictionary']);
					handleClose();
				}
			})
			.catch((error) => {
				alert(localisedStrings['failure-renaming-dictionary'] + '\n' + error);
				handleClose();
			});
	}

	if (dictionaries[index])
		return (
			<FormDialogue
				opened={opened}
				setOpened={setOpened}
				title={localisedStrings['library-screen-rename-dictionary-dialogue-title']}
				content=''
				originalValue={dictionaries[index].displayName}
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
				title={localisedStrings['library-screen-rename-dictionary-dialogue-title']}
			/>	
		);
}
