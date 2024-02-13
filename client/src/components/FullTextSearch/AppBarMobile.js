import React from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import useScrollTrigger from '@mui/material/useScrollTrigger';
import Slide from '@mui/material/Slide';
import MenuButton from '../common/MenuButton';
import FtsInput from './FtsInput';
import ArticlesButton from './ArticlesButton';
import { useFtsContext } from './FtsContext';

export default function AppBarMobile() {
	const { queryContentRef } = useFtsContext();
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
						<FtsInput />
						<ArticlesButton />
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
