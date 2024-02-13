import React from 'react';
import Box from '@mui/material/Box';
import WordList from './WordList';
import ArticleView from './ArticleView';
import { useAnkiContext } from './AnkiContext';

export default function AnkiContentMobile() {
	const { showingArticle, ankiContentRef } = useAnkiContext();

	return (
		<Box
			width='100%'
			height='100%'
			overflow='scroll'
			ref={ankiContentRef}
		>
			{showingArticle ? <ArticleView /> : <WordList />}
		</Box>
	);
}