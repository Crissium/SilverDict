import React from 'react';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import useMediaQuery from '@mui/material/useMediaQuery';
import { FtsProvider } from './FullTextSearch/FtsContext';
import AppBarDesktop from './FullTextSearch/AppBarDesktop';
import AppBarMobile from './FullTextSearch/AppBarMobile';
import ArticlesPane from './FullTextSearch/ArticlesPane';
import ArticleView from './FullTextSearch/ArticleView';
import ArticlesDialogue from './FullTextSearch/ArticlesDialogue';
import { IS_DESKTOP_MEDIA_QUERY } from '../utils';

export default function FtsScreen() {
	const isDesktop = useMediaQuery(IS_DESKTOP_MEDIA_QUERY);

	if (isDesktop)
		return (
			<FtsProvider>
				<Stack height='100vh' sx={{display: 'flex', flexDirection: 'column'}}>
					<AppBarDesktop />
					<Stack
						direction='row'
						spacing={0.5}
						sx={{flexGrow: 1, overflow: 'auto', border: '1px solid #ccc'}}
					>
						<ArticlesPane />
						<Box width={0.7} height='100%' overflow='scroll' sx={{border: '1px solid #ccc'}}>
							<ArticleView />
						</Box>
					</Stack>
				</Stack>
			</FtsProvider>
		);
	else
		return (
			<FtsProvider>
				<AppBarMobile />
				<ArticleView />
				<ArticlesDialogue />
			</FtsProvider>
		);
}
