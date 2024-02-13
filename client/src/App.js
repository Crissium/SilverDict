import React from 'react';
import { Routes, Route } from 'react-router-dom';
import DrawerContent from './DrawerContent';
import QueryScreen from './components/QueryScreen';
import AnkiScreen from './components/AnkiScreen';
import FtsScreen from './components/FtsScreen';
import LibraryScreen from './components/LibraryScreen';
import DictionariesTab from './components/Library/DictionariesTab';
import GroupsTab from './components/Library/GroupsTab';
import SourcesTab from './components/Library/SourcesTab';
import SettingsScreen from './components/SettingsScreen';
import { AppProvider } from './AppContext';

export default function App() {
	return (
		<AppProvider>
			<Routes>
				<Route index element={<QueryScreen />} />
				<Route path='anki' element={<AnkiScreen />} />
				<Route path='fts' element={<FtsScreen />} />
				<Route path='library' element={<LibraryScreen />}>
					<Route index element={<DictionariesTab />} />
					<Route path='dictionaries' element={<DictionariesTab />} />
					<Route path='groups' element={<GroupsTab />} />
					<Route path='sources' element={<SourcesTab />} />
				</Route>
				<Route path='settings' element={<SettingsScreen />} />
			</Routes>
			<DrawerContent />
		</AppProvider>
	);
}
