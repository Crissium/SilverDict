import React from 'react';
import Box from '@mui/material/Box';
import useMediaQuery from '@mui/material/useMediaQuery';
import { IS_DESKTOP_MEDIA_QUERY } from '../../utils';
import GroupsTable from './Groups/GroupsTable';
import GroupsCards from './Groups/GroupsCards';

export default function GroupsTab() {
	const isDesktop = useMediaQuery(IS_DESKTOP_MEDIA_QUERY);

	if (isDesktop)
		return (
			<GroupsTable />
		);
	else
		return (
			<Box maxHeight={1} overflow='scroll'>
				<GroupsCards />
			</Box>
		);
}
