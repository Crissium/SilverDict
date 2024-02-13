import React from 'react';
import FormDialogue from '../common/FormDialogue';
import { API_PREFIX } from '../../config';
import { useAppContext } from '../../AppContext';
import { JSON_HEADER, loadJson } from '../../utils';
import { localisedStrings } from '../../l10n';

export default function HistorySizeDialogue(props) {
	const { opened, setOpened } = props;
	const { setHistory, sizeHistory, setSizeHistory } = useAppContext();

	function handleSubmit(sizeBuffer) {
		let newSize;
		try {
			newSize = parseInt(sizeBuffer);
			newSize = Math.max(newSize, 0);
		} catch (error) {
			alert(localisedStrings['alert-invalid-number']);
			return;
		}

		fetch(`${API_PREFIX}/management/history_size`, {
			method: 'PUT',
			headers: JSON_HEADER,
			body: JSON.stringify({ size: newSize })
		})
			.then(loadJson)
			.then((data) => {
				setHistory(data);
				setSizeHistory(newSize);
			})
			.catch((error) => {
				alert(localisedStrings['failure-changing-size-history'] + '\n' + error);
			})
			.finally(() => {
				setOpened(false);
			});
	}

	return (
		<FormDialogue
			opened={opened}
			setOpened={setOpened}
			title={localisedStrings['settings-screen-change-size-history-dialogue-title']}
			content={localisedStrings['settings-screen-change-size-history-dialogue-content']}
			originalValue={sizeHistory.toString()}
			handleSubmittedData={handleSubmit}
			inputType='number'
			placeholder='100'
			autoCapitalise='off'
		/>
	);
}
