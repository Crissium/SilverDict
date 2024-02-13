import React from 'react';
import ConfirmationDialogue from '../common/ConfirmationDialogue';
import { API_PREFIX } from '../../config';
import { useAppContext } from '../../AppContext';
import { loadJson } from '../../utils';
import { localisedStrings } from '../../l10n';

export default function ClearHistoryDialogue(props) {
	const { opened, setOpened } = props;
	const { setHistory } = useAppContext();

	function handleConfirm() {
		fetch(`${API_PREFIX}/management/history`, {
			method: 'DELETE'
		})
			.then(loadJson)
			.then((data) => {
				setHistory(data);
			})
			.catch((error) => {
				alert(localisedStrings['failure-clearing-history'] + '\n' + error);
			});
	}

	return (
		<ConfirmationDialogue
			opened={opened}
			setOpened={setOpened}
			title={localisedStrings['settings-screen-clear-history-dialogue-title']}
			content={localisedStrings['settings-screen-clear-history-dialogue-confirmation']}
			onConfirm={handleConfirm}
		/>
	);
}
