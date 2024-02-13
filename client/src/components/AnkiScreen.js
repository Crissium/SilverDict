import React from 'react';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import useMediaQuery from '@mui/material/useMediaQuery';
import { AnkiProvider } from './Anki/AnkiContext';
import ArticleView from './Anki/ArticleView';
import DictionariesPane from './Anki/DictionariesPane';
import DictionariesDialogue from './Anki/DictionariesDialogue';
import AnkiInput from './Anki/AnkiInput';
import WordList from './Anki/WordList';
import AppBarDesktop from './Anki/AppBarDesktop';
import AppBarMobile from './Anki/AppBarMobile';
import AnkiContentMobile from './Anki/AnkiContentMobile';
import { IS_DESKTOP_MEDIA_QUERY } from '../utils';

export default function AnkiScreen() {
	const isDesktop = useMediaQuery(IS_DESKTOP_MEDIA_QUERY);

	if (isDesktop)
		return (
			<AnkiProvider>
				<Stack height='100vh' sx={{display: 'flex', flexDirection: 'column'}}>
					<AppBarDesktop />
					<Stack
						direction='row'
						spacing={0.5}
						sx={{flexGrow: 1, overflow: 'auto', border: '1px solid #ccc'}}
					>
						<Stack width={0.2} height='100%' overflow='scroll' padding='0.5em'>
							<AnkiInput />
							<WordList />
						</Stack>
						<Box width={0.5} height='100%' overflow='scroll' sx={{border: '1px solid #ccc'}}>
							<ArticleView />
						</Box>
						<DictionariesPane />
					</Stack>
				</Stack>
			</AnkiProvider>
		);
	else
		return (
			<AnkiProvider>
				<Stack height='100vh'>
					<AppBarMobile />
					<AnkiContentMobile />
				</Stack>
				<DictionariesDialogue />
			</AnkiProvider>
		);
}