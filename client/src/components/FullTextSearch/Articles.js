import React from 'react';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import { useAppContext } from '../../AppContext';
import { useFtsContext } from './FtsContext';
import { isRTL } from '../../utils';

function ArticleListItem(props) {
	const { id, displayName } = props;
	const { setArticlesDialogueOpened } = useFtsContext();

	function navigateToArticle(id) {
		setArticlesDialogueOpened(false);
		const art = document.getElementById(id);
		if (art) {
			art.scrollIntoView();
		}
	}

	return (
		<ListItem key={id}>
			<ListItemButton onClick={() => navigateToArticle(id)}>
				<ListItemText
					primary={displayName}
					primaryTypographyProps={{
						dir: isRTL(displayName) ? 'rtl' : 'ltr'
					}}
				/>
			</ListItemButton>
		</ListItem>
	);
}

export default function Articles() {
	const { dictionaries } = useAppContext();
	const { articlesFound } = useFtsContext();

	function getDisplayNameOfDict(name) {
		try {
			return dictionaries.filter((dict) => dict.name === name)[0].displayName;
		} catch (error) {
			return '';
		}
	}

	if (articlesFound.length > 0)
		return (
			<List
				style={{flexShrink: 1, flexGrow: 1, overflow: 'auto'}}
			>
				{articlesFound.map((a) => 
					<ArticleListItem
						id={`${a.dict}__${a.word}`}
						displayName={`${getDisplayNameOfDict(a.dict)}: ${a.word}`}
					/>
				)}
			</List>
		);
	else
		return (
			<List>
				{dictionaries.map((dict) => (
					<ArticleListItem
						id={dict.name}
						displayName={dict.displayName}
					/>
				))}
			</List>
		);
}
