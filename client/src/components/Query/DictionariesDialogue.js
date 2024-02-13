import React from 'react';
import Dialog from '@mui/material/Dialog';
import { useQueryContext } from './QueryContext';
import Dictionaries from './Dictionaries';

export default function DictionariesDialogue() {
	const { dictionariesDialogueOpened, setDictionariesDialogueOpened } = useQueryContext();

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
