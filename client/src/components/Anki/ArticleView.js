import React from 'react';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useAnkiContext } from './AnkiContext';
import { IS_DESKTOP_MEDIA_QUERY } from '../../utils';

export default function ArticleView() {
	const { article, articleViewRef } = useAnkiContext();
	const isDesktop = useMediaQuery(IS_DESKTOP_MEDIA_QUERY);

	return (
		<>
			<style>
				{`
				.article-block {
					font-size: 1.1em;
					line-height: 1.3em;
					padding-bottom: 10px;
					border-top: 2px solid #ccc;
					border-bottom: 2px solid #ccc;
					margin-top: 10px;
					margin-bottom: 10px;
				}
				
				hr {
					border: none;
					border-top: 0.5px solid #ccc;
					width: 98%;
				}
				`}
			</style>
			<div
				ref={articleViewRef}
				dangerouslySetInnerHTML={{ __html: article }}
				style={isDesktop
					? { paddingLeft: '1em', paddingRight: '1em' }
					: { paddingLeft: '1em', paddingRight: '1em', width: '100vw', overflowX: 'scroll' }}
			/>
		</>
	);
}
