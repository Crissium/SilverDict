import React from 'react';
import Dialog from '@mui/material/Dialog';
import { useAnkiContext } from './AnkiContext';
import Dictionaries from './Dictionaries';

export default function DictionariesDialogue() {
	const { dictionariesDialogueOpened, setDictionariesDialogueOpened } = useAnkiContext();

	return (
		<Dialog
			open={dictionariesDialogueOpened}
			onClose={() => setDictionariesDialogueOpened(false)}
			fullWidth
		>
			<Dictionaries />
		</Dialog>
	);
}
