import React, { useState } from 'react';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import AddIcon from '@mui/icons-material/Add';
import RefreshIcon from '@mui/icons-material/Refresh';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import { Link, useLocation } from 'react-router-dom';
import MenuButton from '../common/MenuButton';
import AddDictionaryDialogue from './Dictionaries/AddDictionaryDialogue';
import AddGroupDialogue from './Groups/AddGroupDialogue';
import AddSourceDialogue from './Sources/AddSourceDialogue';
import ProgressDialogue from '../common/ProgressDialogue';
import { API_PREFIX } from '../../config';
import { useAppContext } from '../../AppContext';
import { loadJson, dictionarySnake2Camel } from '../../utils';
import { localisedStrings } from '../../l10n';

export default function Appbar() {
	const location = useLocation();
	const routes = [
		{
			route: '/library/dictionaries',
			title: localisedStrings['library-screen-dictionaries-tab-title']
		},
		{
			route: '/library/groups',
			title: localisedStrings['library-screen-groups-tab-title']
		},
		{
			route: '/library/sources',
			title: localisedStrings['library-screen-sources-tab-title']
		}
	];

	const { setDictionaries, setGroupings } = useAppContext();
	const [addDictionaryDialogueOpened, setAddDictionaryDialogueOpened] = useState(false);
	const [addGroupDialogueOpened, setAddGroupDialogueOpened] = useState(false);
	const [addSourceDialogueOpened, setAddSourceDialogueOpened] = useState(false);
	const [rescanDialogueOpened, setRescanDialogueOpened] = useState(false);

	function handleRescan() {
		setRescanDialogueOpened(true);
		fetch(`${API_PREFIX}/management/scan`)
			.then(loadJson)
			.then((data) => {
				setDictionaries(data['dictionaries'].map(dictionarySnake2Camel));
				setGroupings(data['groupings']);
			})
			.catch((error) => {
				alert(localisedStrings['failure-rescanning-sources'] + '\n' + error);
			})
			.finally(() => {
				setRescanDialogueOpened(false);
			});
	}

	const buttons = {
		'/library/dictionaries': (
			<IconButton
				onClick={() => setAddDictionaryDialogueOpened(true)}
			>
				<AddIcon />
			</IconButton>
		),
		'/library/groups': (
			<IconButton
				onClick={() => setAddGroupDialogueOpened(true)}
			>
				<AddIcon />
			</IconButton>
		),
		'/library/sources': (
			<>
				<IconButton
					onClick={handleRescan}
				>
					<RefreshIcon />
				</IconButton>
				<IconButton
					onClick={() => setAddSourceDialogueOpened(true)}
				>
					<AddIcon />
				</IconButton>
			</>
		)
	};

	return (
		<>
			<AppBar position='static' sx={{flexShrink: 1}}>
				<Toolbar sx={{flex: 1}}>
					<MenuButton />
					<Typography variant='h6' component='div' sx={{flexGrow: 1}}>
						{localisedStrings['library-screen-title']}
					</Typography>
					{buttons[location.pathname]}
				</Toolbar>
				<Toolbar>
					<ButtonGroup fullWidth>
						{routes.map((route, index) => {
							return (
								<Button
									key={index}
									component={Link}
									to={route.route}
									variant={location.pathname === route.route ? 'contained' : 'text'}
									color='inherit'
									disableElevation
								>
									{route.title}
								</Button>
							);
						})}
					</ButtonGroup>
				</Toolbar>
			</AppBar>
			<AddDictionaryDialogue
				opened={addDictionaryDialogueOpened}
				setOpened={setAddDictionaryDialogueOpened}
			/>
			<AddGroupDialogue
				opened={addGroupDialogueOpened}
				setOpened={setAddGroupDialogueOpened}
			/>
			<AddSourceDialogue
				opened={addSourceDialogueOpened}
				setOpened={setAddSourceDialogueOpened}
			/>
			<ProgressDialogue
				opened={rescanDialogueOpened}
				title={localisedStrings['library-screen-rescan-sources-dialogue-title']}
			/>
		</>
	);
}
