import React from 'react';
import IconButton from '@mui/material/IconButton';
import CollectionsBookmarkIcon from '@mui/icons-material/CollectionsBookmark';
import { useQueryContext } from './QueryContext';

export default function DictionariesButton() {
	const { setDictionariesDialogueOpened } = useQueryContext();

	return (
		<IconButton
			onClick={() => setDictionariesDialogueOpened(true)}
		>
			<CollectionsBookmarkIcon />
		</IconButton>
	);
}