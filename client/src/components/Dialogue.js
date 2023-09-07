import React from 'react';

export function Dialogue(props) {
	const { id, icon, opened, setOpened, children } = props;

	return (
		<>
			<button onClick={() => setOpened(true)}>{icon}</button>
			{opened &&
			<div className='overlay'>
				<div className='dialogue' id={id}>
					<button id='dialogue-close'  onClick={() => setOpened(false)}>✕</button>
					{children}
				</div>
			</div>}
		</>
	);
}
