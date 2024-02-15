import React, { useState } from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Appbar from './Settings/Appbar';
import ClearHistoryDialogue from './Settings/ClearHistoryDialogue';
import HistorySizeDialogue from './Settings/HistorySizeDialogue';
import SuggestionSizeDialogue from './Settings/SuggestionSizeDialogue';
import ProgressDialogue from './common/ProgressDialogue';
import { API_PREFIX } from '../config';
import { useAppContext } from '../AppContext';
import { loadJson } from '../utils';
import { localisedStrings } from '../l10n';

export default function SettingsScreen() {
	const { history, sizeHistory, sizeSuggestion } = useAppContext();
	const [clearHistoryDialogueOpened, setClearHistoryDialogueOpened] = useState(false);
	const [historySizeDialogueOpened, setHistorySizeDialogueOpened] = useState(false);
	const [suggestionSizeDialogueOpened, setSuggestionSizeDialogueOpened] = useState(false);
	const [ngramDialogueOpened, setNgramDialogueOpened] = useState(false);
	const [ftsIndexDialogueOpened, setFtsIndexDialogueOpened] = useState(false);

	function exportHistory() {
		const historyBlob = new Blob([JSON.stringify(history)], { type: 'application/json' });
		const link = document.createElement('a');
		link.href = URL.createObjectURL(historyBlob);
		link.download = 'history.json';
		link.click();
		URL.revokeObjectURL(historyBlob);
	}

	function createNgramIndex() {
		setNgramDialogueOpened(true);
		fetch(`${API_PREFIX}/management/create_ngram_table`)
			.then(loadJson)
			.then((data) => {
				if (data['success']) {
					alert(localisedStrings['alert-ngram-index-created']);
				}
			})
			.catch((error) => {
				alert(localisedStrings['failure-creating-ngram-index'] + '\n' + error);
			})
			.finally(() => {
				setNgramDialogueOpened(false);
			});
	}

	function createFtsIndex() {
		setFtsIndexDialogueOpened(true);
		fetch(`${API_PREFIX}/management/create_xapian_index`)
			.then(loadJson)
			.then((data) => {
				if (data['success']) {
					alert(localisedStrings['alert-full-text-search-index-created']);
				}
			})
			.catch((error) => {
				alert(localisedStrings['failure-creating-full-text-search-index'] + '\n' + error);
			})
			.finally(() => {
				setFtsIndexDialogueOpened(false);
			});
	}

	return (
		<>
			<Stack
				height='100vh'
				sx={{display: 'flex', flexDirection: 'column'}}
			>
				<Appbar />
				<Box height={1} overflow='scroll'>
					<List>
						<ListItem>
							<ListItemButton
								onClick={exportHistory}
							>
								<ListItemText
									primary={localisedStrings['settings-screen-export-history']}
								/>
							</ListItemButton>
						</ListItem>
						<ListItem>
							<ListItemButton
								onClick={() => setClearHistoryDialogueOpened(true)}
							>
								<ListItemText
									primary={localisedStrings['settings-screen-clear-history-dialogue-title']}
								/>
							</ListItemButton>
						</ListItem>
						<ListItem>
							<ListItemButton
								onClick={() => setHistorySizeDialogueOpened(true)}
							>
								<ListItemText
									primary={localisedStrings['settings-screen-change-size-history-dialogue-title']}
									secondary={sizeHistory.toString()}
								/>
							</ListItemButton>
						</ListItem>
						<ListItem>
							<ListItemButton
								onClick={() => setSuggestionSizeDialogueOpened(true)}
							>
								<ListItemText
									primary={localisedStrings['settings-screen-change-size-suggestion-dialogue-title']}
									secondary={sizeSuggestion.toString()}
								/>
							</ListItemButton>
						</ListItem>
						<ListItem>
							<ListItemButton
								onClick={createNgramIndex}
							>
								<ListItemText
									primary={localisedStrings['settings-screen-create-ngram-index']}
									secondary={localisedStrings['settings-screen-reminder-slowness']}
								/>
							</ListItemButton>
						</ListItem>
						<ListItem>
							<ListItemButton
								onClick={createFtsIndex}
							>
								<ListItemText
									primary={localisedStrings['settings-screen-create-full-text-search-index']}
									secondary={localisedStrings['settings-screen-reminder-slowness']}
								/>
							</ListItemButton>
						</ListItem>
					</List>
				</Box>
			</Stack>
			<ClearHistoryDialogue
				opened={clearHistoryDialogueOpened}
				setOpened={setClearHistoryDialogueOpened}
			/>
			<HistorySizeDialogue
				opened={historySizeDialogueOpened}
				setOpened={setHistorySizeDialogueOpened}
			/>
			<SuggestionSizeDialogue
				opened={suggestionSizeDialogueOpened}
				setOpened={setSuggestionSizeDialogueOpened}
			/>
			<ProgressDialogue
				opened={ngramDialogueOpened}
				title={localisedStrings['settings-screen-creating-ngram-index']}
			/>
			<ProgressDialogue
				opened={ftsIndexDialogueOpened}
				title={localisedStrings['settings-screen-creating-full-text-search-index']}
			/>
		</>
	);
}
