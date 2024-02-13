import React from 'react';
import FormDialogue from '../common/FormDialogue';
import { API_PREFIX } from '../../config';
import { useAppContext } from '../../AppContext';
import { JSON_HEADER, loadJson } from '../../utils';
import { localisedStrings } from '../../l10n';

export default function SuggestionSizeDialogue(props) {
	const { opened, setOpened } = props;
	const { sizeSuggestion, setSizeSuggestion } = useAppContext();

	function handleSubmit(sizeBuffer) {
		let newSize;
		try {
			newSize = parseInt(sizeBuffer);
			newSize = Math.max(newSize, 1);
		} catch (error) {
			alert(localisedStrings['alert-invalid-number']);
			return;
		}

		fetch(`${API_PREFIX}/management/num_suggestions`, {
			method: 'PUT',
			headers: JSON_HEADER,
			body: JSON.stringify({ size: newSize })
		})
			.then(loadJson)
			.then((data) => {
				setSizeSuggestion(data['size']);
			})
			.catch((error) => {
				alert(localisedStrings['failure-changing-size-suggestion'] + '\n' + error);
			})
			.finally(() => {
				setOpened(false);
			});
	}

	return (
		<FormDialogue
			opened={opened}
			setOpened={setOpened}
			title={localisedStrings['settings-screen-change-size-suggestion-dialogue-title']}
			content={localisedStrings['settings-screen-change-size-suggestion-dialogue-content']}
			originalValue={sizeSuggestion.toString()}
			handleSubmittedData={handleSubmit}
			inputType='number'
			placeholder='10'
			autoCapitalise='off'
		/>
	);
}
