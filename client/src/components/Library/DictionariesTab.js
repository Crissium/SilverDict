import React from 'react';
import useMediaQuery from '@mui/material/useMediaQuery';
import { IS_DESKTOP_MEDIA_QUERY } from '../../utils';
import DictionariesTable from './Dictionaries/DictionariesTable';
import DictionariesList from './Dictionaries/DictionariesList';

export default function DictionariesTab() {
	const isDesktop = useMediaQuery(IS_DESKTOP_MEDIA_QUERY);

	if (isDesktop)
		return (
			<DictionariesTable />
		);
	else
		return (
			<DictionariesList />
		);
}