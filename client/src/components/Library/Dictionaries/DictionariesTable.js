import React, { useEffect, useState } from 'react';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import EditButton from '../../common/EditButton';
import RenameDictionaryDialogue from './RenameDictionaryDialogue';
import DeleteButton from '../../common/DeleteButton';
import DeleteDictionaryDialogue from './DeleteDictionaryDialogue';
import { API_PREFIX } from '../../../config';
import { JSON_HEADER, dictionarySnake2Camel, dictionaryCamel2Snake, loadJson } from '../../../utils';
import { useAppContext } from '../../../AppContext';
import { getHeadwordCount } from './utils';
import { localisedStrings } from '../../../l10n';

export default function DictionariesTable() {
	const { dictionaries, setDictionaries } = useAppContext();
	const [headwordCounts, setHeadwordCounts] = useState({});
	const [renameDialogueOpened, setRenameDialogueOpened] = useState(false);
	const [renamedDictionaryIndex, setRenamedDictionaryIndex] = useState(-1);
	const [deleteDialogueOpened, setDeleteDialogueOpened] = useState(false);
	const [toBeDeletedIndex, setToBeDeletedIndex] = useState(-1);

	async function getAllHeadwordCounts(names) {
		const promises = names.map(name => getHeadwordCount(name));
		const counts = await Promise.all(promises);
		return names.reduce((acc, name, index) => ({ ...acc, [name]: counts[index] }), {});
	}

	useEffect(function() {
		if (dictionaries.length > 0) {
			const names = dictionaries.map((d) => (d.name));
			const missing = names.filter((name) => !(name in headwordCounts));
			if (missing.length > 0) {
				getAllHeadwordCounts(missing)
					.then((newCounts) => {
						setHeadwordCounts({ ...headwordCounts, ...newCounts });
					});
			}
		}
	}, [dictionaries, headwordCounts]);

	function handleDrag(result) {
		if (!result.destination)
			return;

		const items = Array.from(dictionaries);
		const [reorderedItem] = items.splice(result.source.index, 1);
		items.splice(result.destination.index, 0, reorderedItem);
		
		fetch(`${API_PREFIX}/management/dictionaries`, {
			method: 'PUT',
			headers: JSON_HEADER,
			body: JSON.stringify(items.map(dictionaryCamel2Snake))
		})
			.then(loadJson)
			.then((data) => {
				setDictionaries(data.map(dictionarySnake2Camel));
			})
			.catch((error) => {
				alert(localisedStrings['failure-reordering-dictionaries'] + '\n' + error);
			});
	}

	function handleRenameDialogueOpen(index) {
		setRenamedDictionaryIndex(index);
		setRenameDialogueOpened(true);
	}

	function handleRenameDialogueClose() {
		setRenamedDictionaryIndex(-1);
		setRenameDialogueOpened(false);
	}

	function handleDeleteDialogueOpen(index) {
		setToBeDeletedIndex(index);
		setDeleteDialogueOpened(true);
	}

	function handleDeleteDialogueClose() {
		setToBeDeletedIndex(-1);
		setDeleteDialogueOpened(false);
	}

	if (!dictionaries)
		return (
			<Typography
				variant='body'
			>
				{localisedStrings['generic-loading']}
			</Typography>
		);
	else
		return (
			<DragDropContext onDragEnd={handleDrag}>
				<TableContainer>
					<Table stickyHeader>
						<TableHead>
							<TableRow>
								<TableCell sx={{ fontWeight: 'bold' }}>
									{localisedStrings['library-screen-dictionaries-table-head-name']}
								</TableCell>
								<TableCell sx={{ fontWeight: 'bold' }}>
									{localisedStrings['library-screen-dictionaries-table-head-filename']}
								</TableCell>
								<TableCell sx={{ fontWeight: 'bold' }}>
									{localisedStrings['library-screen-dictionaries-table-head-headword-count']}
								</TableCell>
								<TableCell sx={{ fontWeight: 'bold' }}>
									{localisedStrings['library-screen-dictionaries-table-head-actions']}
								</TableCell>
							</TableRow>
						</TableHead>
						<Droppable droppableId='dictionaries'>
							{(provided) => (
								<TableBody {...provided.droppableProps} ref={provided.innerRef}>
									{dictionaries.map((d, index) => (
										<Draggable key={d.name} draggableId={d.name} index={index}>
											{(provided) => (
												<TableRow
													{...provided.draggableProps}
													{...provided.dragHandleProps}
													ref={provided.innerRef}
												>
													<TableCell>{d.displayName}</TableCell>
													<TableCell>{d.filename}</TableCell>
													<TableCell>
														{headwordCounts[d.name] ||
														localisedStrings['generic-loading']}
													</TableCell>
													<TableCell sx={{display: 'flex'}}>
														<EditButton
															handleClick={() => handleRenameDialogueOpen(index)}
														/>
														<DeleteButton
															handleClick={() => handleDeleteDialogueOpen(index)}
														/>
													</TableCell>
												</TableRow>
											)}
										</Draggable>
									))}
									{provided.placeholder}
								</TableBody>
							)}
						</Droppable>
					</Table>
				</TableContainer>
				<RenameDictionaryDialogue
					opened={renameDialogueOpened}
					setOpened={setRenameDialogueOpened}
					handleClose={handleRenameDialogueClose}
					index={renamedDictionaryIndex}
				/>
				<DeleteDictionaryDialogue
					opened={deleteDialogueOpened}
					setOpened={setDeleteDialogueOpened}
					handleClose={handleDeleteDialogueClose}
					index={toBeDeletedIndex}
				/>
			</DragDropContext>
		);
}
