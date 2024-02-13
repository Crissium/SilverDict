import React from 'react';
import Stack from '@mui/material/Stack';
import Box from '@mui/material/Box';
import useMediaQuery from '@mui/material/useMediaQuery';
import { QueryProvider } from './Query/QueryContext';
import ArticleView from './Query/ArticleView';
import DictionariesPane from './Query/DictionariesPane';
import DictionariesDialogue from './Query/DictionariesDialogue';
import QueryInput from './Query/QueryInput';
import WordList from './Query/WordList';
import AppBarDesktop from './Query/AppBarDesktop';
import AppBarMobile from './Query/AppBarMobile';
import QueryContentMobile from './Query/QueryContentMobile';
import { IS_DESKTOP_MEDIA_QUERY } from '../utils';

export default function QueryScreen() {
	const isDesktop = useMediaQuery(IS_DESKTOP_MEDIA_QUERY);
	
	if (isDesktop)
		return (
			<QueryProvider>
				<Stack height='100vh' sx={{display: 'flex', flexDirection: 'column'}}>
					<AppBarDesktop />
					<Stack
						direction='row'
						spacing={0.5}
						sx={{flexGrow: 1, overflow: 'auto', border: '1px solid #ccc'}}
					>
						<Stack width={0.2} height='100%' overflow='scroll' padding='0.5em'>
							<QueryInput />
							<WordList />
						</Stack>
						<Box width={0.5} height='100%' overflow='scroll' sx={{border: '1px solid #ccc'}}>
							<ArticleView />
						</Box>
						<DictionariesPane />
					</Stack>
				</Stack>
			</QueryProvider>
		);
	else
		return (
			<QueryProvider>
				<AppBarMobile />
				<QueryContentMobile />
				<DictionariesDialogue />
			</QueryProvider>
		);
}
