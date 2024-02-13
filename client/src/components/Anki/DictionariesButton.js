import React from 'react';
import IconButton from '@mui/material/IconButton';
import CollectionsBookmarkIcon from '@mui/icons-material/CollectionsBookmark';
import { useAnkiContext } from './AnkiContext';

export default function DictionariesButton() {
	const { setDictionariesDialogueOpened } = useAnkiContext();

	return (
		<IconButton
			onClick={() => setDictionariesDialogueOpened(true)}
		>
			<CollectionsBookmarkIcon />
		</IconButton>
	);
}