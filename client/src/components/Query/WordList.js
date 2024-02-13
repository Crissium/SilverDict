import React, { useCallback, useEffect, useState } from 'react';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import { useAppContext } from '../../AppContext';
import { useQueryContext } from './QueryContext';
import { isRTL } from '../../utils';

function WordListItem(props) {
	const { displayingHistory, index, word, selectedIndex, setSelectedIndex } = props;
	const isSelected = selectedIndex === index;
	const wordIsRTL = isRTL(word);
	const { search, setShowingArticleView } = useQueryContext();

	function handleClick() {
		if (displayingHistory) {
			setSelectedIndex(0);
		} else {
			setSelectedIndex(index);
		}
		search(word);
		setShowingArticleView(true, true);
	}

	return (
		<ListItem disablePadding key={index}>
			<ListItemButton
				selected={isSelected}
				onClick={handleClick}
			>
				<ListItemText
					primary={word}
					primaryTypographyProps={{
						dir: wordIsRTL ? 'rtl' : 'ltr',
						fontWeight: isSelected ? 'bold' : 'normal'
					}}
				/>
			</ListItemButton>
		</ListItem>
	);
}

export default function WordList() {
	const { history } = useAppContext();
	const { searchTerm, inputRef, search, suggestions, setShowingArticleView } = useQueryContext();
	const displayingHistory = searchTerm.length === 0;
	const wordsToDisplay = displayingHistory ? history : suggestions;

	const [selectedIndex, setSelectedIndex] = useState(0);

	useEffect(function() {
		if (selectedIndex >= wordsToDisplay.length) {
			setSelectedIndex(wordsToDisplay.length - 1);
		}
	}, [wordsToDisplay.length]);

	useEffect(function() {
		if (displayingHistory) {
			setSelectedIndex(0);
		}
	}, [displayingHistory]);

	const handleKeyDown = useCallback(function (e) {
		if (document.activeElement === inputRef.current) {
			if (e.key === 'ArrowDown') {
				e.preventDefault();
				if (selectedIndex < wordsToDisplay.length) {
					setSelectedIndex(selectedIndex + 1);
				}
			} else if (e.key === 'ArrowUp') {
				e.preventDefault();
				if (selectedIndex > 0) {
					setSelectedIndex(selectedIndex - 1);
				}
			} else if (e.key === 'Enter') {
				search(wordsToDisplay[selectedIndex]);
				if (displayingHistory) {
					setSelectedIndex(0);
				}
				setShowingArticleView(true, true);
			}
		}
	}, [selectedIndex, setSelectedIndex, displayingHistory, wordsToDisplay]);

	useEffect(function() {
		document.addEventListener('keydown', handleKeyDown);

		return () => {
			document.removeEventListener('keydown', handleKeyDown);
		};
	}, [handleKeyDown]);

	return (
		<List
			style={{flexShrink: 1, flexGrow: 1, overflow: 'auto'}}
		>
			{wordsToDisplay.map((word, index) => (
				<WordListItem
					displayingHistory={displayingHistory}
					index={index}
					word={word}
					selectedIndex={selectedIndex}
					setSelectedIndex={setSelectedIndex}
				/>
			))}
		</List>
	);
}
