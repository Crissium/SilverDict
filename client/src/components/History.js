import React from 'react';
import { API_PREFIX } from '../config';
import { loadDataFromYamlResponse } from '../utils';

export function History(props) {
	const { showHeadingsAndButtons, history, setHistory, historySize, search } = props;

	function handleHistoryClear() {
		fetch(`${API_PREFIX}/management/history`, {
			method: 'DELETE'
		})
			.then(loadDataFromYamlResponse)
			.then((data) => {
				setHistory(data);
			});
	}

	function handleHistoryExport() {
		const historyBlob = new Blob([JSON.stringify(history)], { type: 'application/json' });
		const link = document.createElement('a');
		link.href = URL.createObjectURL(historyBlob);
		link.download = 'history.json';
		link.click();
		URL.revokeObjectURL(historyBlob);
	}

	return (
		<div className='history'>
			{showHeadingsAndButtons && (
				<p className='heading'>
					<strong>History ({history.length}/{historySize})</strong>
					<button
						onClick={handleHistoryClear}
					>
						Clear
					</button>
					<button
						onClick={handleHistoryExport}
					>
						Export
					</button>
				</p>
			)}
			<ul>
				{history.map((item) => (
					<li
						className='clickable'
						key={item}
						onClick={() => search(item)}
					>
						{item}
					</li>
				))}
			</ul>
		</div>
	);
}
