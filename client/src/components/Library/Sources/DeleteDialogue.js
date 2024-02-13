import React from 'react';
import ConfirmationDialogue from '../../common/ConfirmationDialogue';
import LoadingDialogue from '../../common/LoadingDialogue';
import { useAppContext } from '../../../AppContext';
import { API_PREFIX } from '../../../config';
import { JSON_HEADER, loadJson } from '../../../utils';
import { localisedStrings } from '../../../l10n';

export default function DeleteDialogue(props) {
	const { opened, setOpened, handleClose, index } = props;
	const { sources, setSources } = useAppContext();

	function handleConfirm() {
		fetch(`${API_PREFIX}/management/sources`, {
			method: 'DELETE',
			headers: JSON_HEADER,
			body: JSON.stringify({ source: sources[index] })
		})
			.then(loadJson)
			.then((data) => {
				setSources(data);
			})
			.catch((error) => {
				alert(localisedStrings['failure-deleting-source'] + '\n' + error);
			})
			.finally(() => {
				handleClose();
			});
	}

	if (sources[index])
		return (
			<ConfirmationDialogue
				opened={opened}
				setOpened={setOpened}
				title={localisedStrings['library-screen-delete-source-dialogue-title']}
				content={localisedStrings.formatString(
					localisedStrings['library-screen-delete-source-dialogue-confirmation'],
					sources[index]
				)}
				onConfirm={handleConfirm}
			/>
		);
	else
		return (
			<LoadingDialogue
				opened={opened}
				setOpened={setOpened}
				title={localisedStrings['library-screen-delete-source-dialogue-title']}
			/>
		);
}
