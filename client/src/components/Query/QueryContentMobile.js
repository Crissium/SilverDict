import React from 'react';
import WordList from './WordList';
import ArticleView from './ArticleView';
import { useQueryContext } from './QueryContext';

export default function QueryContentMobile() {
	const { showingArticle } = useQueryContext();

	if (showingArticle)
		return (
			<ArticleView />
		);
	else
		return (
			<WordList />
		);
}
