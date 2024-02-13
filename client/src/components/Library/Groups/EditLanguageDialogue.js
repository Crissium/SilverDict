import React from 'react';
import ISO6391 from 'iso-639-1';
import FormDialogue from '../../common/FormDialogue';
import LoadingDialogue from '../../common/LoadingDialogue';
import { API_PREFIX } from '../../../config';
import { useAppContext } from '../../../AppContext';
import { JSON_HEADER, loadJson, getSetFromLangString } from '../../../utils';
import { localisedStrings } from '../../../l10n';

export default function EditLanguageDialogue(props) {
	const { opened, setOpened, handleClose, index } = props;
	const { groups, setGroups } = useAppContext();

	function handleSubmit(langString) {
		const langSet = getSetFromLangString(langString);
		for (const lang of langSet) {
			if (!ISO6391.validate(lang)) {
				alert(localisedStrings.formatString(
					localisedStrings['alert-invalid-language-code'],
					lang
				));
				handleClose();
				return;
			}
		}

		fetch(`${API_PREFIX}/management/group_lang`, {
			method: 'PUT',
			headers: JSON_HEADER,
			body: JSON.stringify({ name: groups[index].name, lang: Array.from(langSet) })
		})
			.then(loadJson)
			.then((data) => {
				setGroups(data);
				handleClose();
			})
			.catch((error) => {
				alert(localisedStrings['failure-editing-group-languages'] + '\n' + error);
				handleClose();
			});
	}

	if (groups[index])
		return (
			<FormDialogue
				opened={opened}
				setOpened={setOpened}
				title={localisedStrings['library-screen-groups-table-actions-edit-languages']}
				content=''
				originalValue={groups[index].lang.join(', ')}
				handleSubmittedData={handleSubmit}
				inputType='text'
				placeholder='en, fr'
				autoCapitalise='off'
			/>
		);
	else
		return (
			<LoadingDialogue
				opened={opened}
				setOpened={setOpened}
				title={localisedStrings['library-screen-groups-table-actions-edit-languages']}
			/>
		);
}
