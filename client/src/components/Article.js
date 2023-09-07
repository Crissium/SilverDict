import React, { useState } from 'react';

export function Article(props) {
	const { article } = props;
	const [fontSize, setFontSize] = useState(1); // in rem

	return (
		<div className='article'>
			<div
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
				-
			</button>
		</div>
	);
}
