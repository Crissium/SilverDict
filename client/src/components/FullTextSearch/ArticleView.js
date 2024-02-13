import React, { useCallback, useEffect, useState } from 'react';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useFtsContext } from './FtsContext';
import { IS_DESKTOP_MEDIA_QUERY } from '../../utils';
import { localisedStrings } from '../../l10n';

export default function ArticleView() {
	const { article, articleViewRef } = useFtsContext();
	const isDesktop = useMediaQuery(IS_DESKTOP_MEDIA_QUERY);
	const [contextMenu, setContextMenu] = useState(null);
	const [selectedText, setSelectedText] = useState('');

	const handleWordClick = useCallback(function (e) {
		let targetEl = e.target;
		while (targetEl !== articleViewRef.current) {
			if (typeof targetEl.onclick === 'function' || targetEl.tagName.toLowerCase() === 'a') {
				// The element has an onClick listener, so do not capture it.
				return;
			}
			targetEl = targetEl.parentNode;
		}

		const selection = window.getSelection();
		let range = selection.getRangeAt(0);
		const node = selection.anchorNode;
		const wordPattern = /^\p{L}*$/u;

		// Extend the range backward until it matches word beginning
		while ((range.startOffset > 0) && range.toString().match(wordPattern)) {
			range.setStart(node, (range.startOffset - 1));
		}
		// Restore the valid word match after overshooting
		if (!range.toString().match(wordPattern)) {
			range.setStart(node, range.startOffset + 1);
		}

		// Extend the range forward until it matches word ending
		while ((range.endOffset < node.length) && range.toString().match(wordPattern)) {
			range.setEnd(node, range.endOffset + 1);
		}
		// Restore the valid word match after overshooting
		if (!range.toString().match(wordPattern)) {
			range.setEnd(node, range.endOffset - 1);
		}

		const word = range.toString().trim();
		if (word.length > 0) {
			setSelectedText(word);

			setContextMenu({
				mouseX: e.clientX + 2,
				mouseY: e.clientY - 6,
			});
		}
	}, [setSelectedText]);

	useEffect(function () {
		if (articleViewRef.current) {
			articleViewRef.current.addEventListener('click', handleWordClick);
		}
		
		return function () {
			if (articleViewRef.current) {
				articleViewRef.current.removeEventListener('click', handleWordClick);
			}
		};
	}, [handleWordClick]);

	function handleSearchInNewTab() {
		window.open(`/?key=${selectedText}`, '_blank');
		setContextMenu(null);
		setSelectedText('');
	}

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
				
				img {
					max-width: 100%;
				}
				
				hr {
					border: none;
					border-top: 0.5px solid #ccc;
					width: 98%;
				}
				
				.dictionary-headings {
					padding-top: 10px;
					padding-bottom: 10px;
					color: darkgreen;
					font-size: 1.5em;
					font-weight: bolder;
				}
				
				audio {
					height: 0.8em;
				}`}
			</style>
			<div
				dangerouslySetInnerHTML={{ __html: article }}
				style={isDesktop
					? { paddingLeft: '1em', paddingRight: '1em' }
					: { paddingLeft: '1em', paddingRight: '1em', width: '100vw', overflowX: 'scroll' }}
				ref={articleViewRef}
			/>
			<Menu
				open={contextMenu !== null}
				onClose={() => setContextMenu(null)}
				anchorReference='anchorPosition'
				anchorPosition={
					contextMenu !== null
						? { top: contextMenu.mouseY, left: contextMenu.mouseX }
						: undefined
				}
			>
				<MenuItem onClick={handleSearchInNewTab}>
					{localisedStrings['article-view-menu-search-in-new-tab']}
				</MenuItem>
			</Menu>
		</>
	);
}
