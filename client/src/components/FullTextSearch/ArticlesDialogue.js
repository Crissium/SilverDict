import React from 'react';
import Dialog from '@mui/material/Dialog';
import { useFtsContext } from './FtsContext';
import Articles from './Articles';

export default function ArticlesDialogue() {
	const { articlesDialogueOpened, setArticlesDialogueOpened } = useFtsContext();

	return (
		<Dialog
			open={articlesDialogueOpened}
			onClose={() => setArticlesDialogueOpened(false)}
			fullWidth
		>
			<Articles />
		</Dialog>
	);
}
