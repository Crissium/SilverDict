import React from 'react';
import Box from '@mui/material/Box';
import Drawer from '@mui/material/Drawer';
import MuiLink from '@mui/material/Link';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import Typography from '@mui/material/Typography';
import SearchIcon from '@mui/icons-material/Search';
import StarIcon from '@mui/icons-material/Star';
import ManageSearchIcon from '@mui/icons-material/ManageSearch';
import CollectionsBookmarkIcon from '@mui/icons-material/CollectionsBookmark';
import SettingsIcon from '@mui/icons-material/Settings';
import { Link, useLocation } from 'react-router-dom';
import { useAppContext } from './AppContext';
import { localisedStrings } from './l10n';

function DrawerItem(props) {
	const icons = {
		'/': <SearchIcon />,
		'/anki': <StarIcon />,
		'/fts': <ManageSearchIcon />,
		'/library/dictionaries': <CollectionsBookmarkIcon />,
		'/settings': <SettingsIcon />
	};

	const { index, route, title, isActive } = props;
	const { setDrawerOpened } = useAppContext();

	return (
		<ListItem key={index}>
			<ListItemButton
				selected={isActive}
				LinkComponent={Link}
				to={route}
				onClick={() => setDrawerOpened(false)}
			>
				<ListItemIcon>
					{icons[route]}
				</ListItemIcon>
				<ListItemText
					primary={title}
					primaryTypographyProps={{
						style: {
							fontWeight: isActive ? 'bold' : 'normal'
						}
					}}
				/>
			</ListItemButton>
		</ListItem>
	);
}

export default function DrawerContent() {
	const { drawerOpened, setDrawerOpened } = useAppContext();
	const routes = [
		{
			route: '/',
			title: localisedStrings['query-screen-title']
		},
		{
			route: '/anki',
			title: localisedStrings['anki-screen-title']
		},
		{
			route: '/fts',
			title: localisedStrings['full-text-search-screen-title']
		},
		{
			route: '/library/dictionaries',
			title: localisedStrings['library-screen-title']
		},
		{
			route: '/settings',
			title: localisedStrings['settings-screen-title']
		}
	];
	const location = useLocation();

	return (
		<Drawer
			anchor='left'
			open={drawerOpened}
			onClose={(e, reason) => setDrawerOpened(false)}
		>
			<List>
				{routes.map((route, index) => (
					<DrawerItem
						index={index}
						route={route.route}
						title={route.title}
						isActive={location.pathname === route.route}
					/>
				))}
			</List>
			<Box sx={{ 
				position: 'absolute',
				bottom: 0,
				width: '100%',
				textAlign: 'center',
				paddingBottom: 3
			}}>
				<Box>
					<MuiLink 
						href='https://silverdict.lecoteauverdoyant.co.uk/' 
						target='_blank' 
						variant='body2' 
						sx={{ display: 'inline-block', marginRight: 0.5 }}
					>
						SilverDict
					</MuiLink>
					<Typography 
						variant='body2' 
						sx={{ display: 'inline-block' }}
					>
						v1.3.0
					</Typography>
				</Box>
				<Box>
					<Typography variant='body2'>
						&copy; <MuiLink variant='body2' href='mailto:blandilyte@gmail.com'>Yi Xing</MuiLink> 2024
					</Typography>
				</Box>
				<Box>
					<Typography variant='body2'>
						{localisedStrings['licence']}
					</Typography>
				</Box>
			</Box>
		</Drawer>
	);
}
