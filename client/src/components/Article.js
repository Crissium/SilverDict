import React, { useState, useEffect } from 'react';

export function Article(props) {
	const { article, setQuery, isMobile, handleGoBack } = props;
	const [fontSize, setFontSize] = useState(1); // in rem

	useEffect(function () {
		const articleElement = document.querySelector('.inner-article');
		articleElement.addEventListener('click', function (event) {
			let targetElement = event.target;

			while (targetElement !== articleElement) {
				if (typeof targetElement.onclick === 'function' || targetElement.tagName === 'A') {
					// The element has an onClick listener, so do not capture it.
					return;
				}
				targetElement = targetElement.parentNode;
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
				setQuery(word);
				if (isMobile) {
					const input = document.querySelector('input');
					input.focus();
				}
			}
		});
	}, []);

	return (
		<div className='article'>
			<div
				className='inner-article'
				style={{ fontSize: `${fontSize}rem` }}
				dangerouslySetInnerHTML={{ __html: article }} />
			<button
				onClick={() => setFontSize(Math.min(2, fontSize + 0.1))}
				id='size-increase'
			>
				+
			</button>
			<button
				onClick={() => setFontSize(Math.max(0.25, fontSize - 0.1))}
				id='size-decrease'
			>
				−
			</button>
			{isMobile && (
				<button
					onClick={() => { handleGoBack(); }}
					id='back-button'
				>
					←
				</button>
			)}
		</div>
	);
}
