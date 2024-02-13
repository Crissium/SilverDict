import React from 'react';
import IconButton from '@mui/material/IconButton';
import CollectionsBookmarkIcon from '@mui/icons-material/CollectionsBookmark';
import { useFtsContext } from './FtsContext';

export default function ArticlesButton() {
	const { setArticlesDialogueOpened } = useFtsContext();

	return (
		<IconButton
			onClick={() => setArticlesDialogueOpened(true)}
		>
			<CollectionsBookmarkIcon />
		</IconButton>
	);
}