import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import useScrollTrigger from '@mui/material/useScrollTrigger';
import Slide from '@mui/material/Slide';
import MenuButton from '../common/MenuButton';
import QueryInput from './QueryInput';
import DictionariesButton from './DictionariesButton';
import { useQueryContext } from './QueryContext';

export default function AppBarMobile() {
	const { queryContentRef } = useQueryContext();

	const trigger = useScrollTrigger();

	return (
		<>
			<Slide
				appear={false}
				direction='down'
				in={!trigger}
			>
				<AppBar>
					<Toolbar>
						<MenuButton />
						<QueryInput />
						<DictionariesButton />
					</Toolbar>
				</AppBar>
			</Slide>
			<Toolbar
				// This dummy toolbar is to prevent the content from being hidden by the AppBar
				ref={queryContentRef}
			/>
		</>
	);
}
