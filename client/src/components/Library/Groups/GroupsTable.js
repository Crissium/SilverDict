import React, { useState } from 'react';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';
import Table from '@mui/material/Table';
import TableBody from '@mui/material/TableBody';
import TableCell from '@mui/material/TableCell';
import TableContainer from '@mui/material/TableContainer';
import TableHead from '@mui/material/TableHead';
import TableRow from '@mui/material/TableRow';
import Typography from '@mui/material/Typography';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import ISO6391 from 'iso-639-1';
import EditLanguageDialogue from './EditLanguageDialogue';
import RenameDialogue from './RenameDialogue';
import DeleteDialogue from './DeleteDialogue';
import EditDictionariesDialogue from './EditDictionariesDialogue';
import { API_PREFIX } from '../../../config';
import { JSON_HEADER, loadJson } from '../../../utils';
import { useAppContext } from '../../../AppContext';
import { localisedStrings } from '../../../l10n';

export default function GroupsTable() {
	const { dictionaries, groups, setGroups, groupings } = useAppContext();
	const [indexLangEdited, setIndexLangEdited] = useState(-1);
	const [editLangDialogueOpened, setEditLangDialogueOpened] = useState(false);
	const [indexRenamed, setIndexRenamed] = useState(-1);
	const [renameDialogueOpened, setRenameDialogueOpened] = useState(false);
	const [indexDeleted, setIndexDeleted] = useState(-1);
	const [deleteDialogueOpened, setDeleteDialogueOpened] = useState(false);
	const [indexDictionariesEdited, setIndexDictionariesEdited] = useState(-1);
	const [editDictsDialogueOpened, setEditDictsDialogueOpened] = useState(false);

	function namesDictsInGroup(index) {
		const names = groupings[groups[index].name];
		const displayNames = [];
		for (const d of dictionaries) {
			if (names.includes(d.name)) {
				displayNames.push(d.displayName);
			}
		}
		return displayNames.join('\n');
	}

	function namesLangsOfGroup(index) {
		return groups[index].lang.map(ISO6391.getNativeName).join('\n');
	}

	function handleDrag(result) {
		if (!result.destination)
			return;

		const items = Array.from(groups);
		const [reorderedItem] = items.splice(result.source.index, 1);
		items.splice(result.destination.index, 0, reorderedItem);
		
		fetch(`${API_PREFIX}/management/groups`, {
			method: 'PUT',
			headers: JSON_HEADER,
			body: JSON.stringify(items)
		})
			.then(loadJson)
			.then((data) => {
				setGroups(data);
			})
			.catch((error) => {
				alert(localisedStrings['failure-reordering-groups'] + '\n' + error);
			});
	}

	function handleEditLangDialogueOpen(index) {
		setIndexLangEdited(index);
		setEditLangDialogueOpened(true);
	}

	function handleEditedLangDialogueClose() {
		setIndexLangEdited(-1);
		setEditLangDialogueOpened(false);
	}

	function handleRenameDialogueOpen(index) {
		setIndexRenamed(index);
		setRenameDialogueOpened(true);
	}

	function handleRenameDialogueClose() {
		setIndexRenamed(-1);
		setEditLangDialogueOpened(false);
	}

	function handleDeleteDialogueOpen(index) {
		setIndexDeleted(index);
		setDeleteDialogueOpened(true);
	}

	function handleDeleteDialogueClose() {
		setIndexDeleted(-1);
		setDeleteDialogueOpened(false);
	}

	function handleEditDictsDialogueOpen(index) {
		setIndexDictionariesEdited(index);
		setEditDictsDialogueOpened(true);
	}

	function handleEditDictsDialogueClose() {
		setIndexDictionariesEdited(-1);
		setEditDictsDialogueOpened(false);
	}

	if (dictionaries && groups && groupings)
		return (
			<DragDropContext onDragEnd={handleDrag}>
				<TableContainer>
					<Table stickyHeader>
						<TableHead>
							<TableRow>
								<TableCell sx={{ fontWeight: 'bold' }}>
									{localisedStrings['library-screen-add-group-dialogue-textfield-name-label']}
								</TableCell>
								<TableCell sx={{ fontWeight: 'bold' }}>
									{localisedStrings['library-screen-add-group-dialogue-textfield-lang-label']}
								</TableCell>
								<TableCell sx={{ fontWeight: 'bold' }}>
									{localisedStrings['library-screen-dictionaries-tab-title']}
								</TableCell>
								<TableCell sx={{ fontWeight: 'bold' }}>
									{localisedStrings['library-screen-dictionaries-table-head-actions']}
								</TableCell>
							</TableRow>
						</TableHead>
						<Droppable droppableId='groups'>
							{(provided) => (
								<TableBody {...provided.droppableProps} ref={provided.innerRef}>
									{groups.map((g, index) => (
										<Draggable key={g.name} draggableId={g.name} index={index}>
											{(provided) => (
												<TableRow
													{...provided.draggableProps}
													{...provided.dragHandleProps}
													ref={provided.innerRef}
												>
													<TableCell>{g.name}</TableCell>
													<TableCell
														sx={{whiteSpace: 'pre-line'}}
													>
														{namesLangsOfGroup(index)}
													</TableCell>
													<TableCell
														sx={{whiteSpace: 'pre-line'}}
													>
														{namesDictsInGroup(index)}
													</TableCell>
													<TableCell>
														<ButtonGroup
															orientation='vertical'
															color='inherit'
														>
															<Button
																disabled={g.name === 'Default Group'}
																onClick={() => {
																	handleRenameDialogueOpen(index);
																}}
															>
																{localisedStrings['generic-rename']}
															</Button>
															<Button
																onClick={() => {
																	handleEditLangDialogueOpen(index);
																}}
															>
																{localisedStrings['library-screen-groups-table-actions-edit-languages']}
															</Button>
															<Button
																onClick={() => {
																	handleEditDictsDialogueOpen(index);
																}}
															>
																{localisedStrings['library-screen-groups-table-actions-edit-dictionaries']}
															</Button>
															<Button
																disabled={g.name === 'Default Group'}
																onClick={() => {
																	handleDeleteDialogueOpen(index);
																}}
															>
																{localisedStrings['generic-delete']}
															</Button>
														</ButtonGroup>
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
				<EditLanguageDialogue
					opened={editLangDialogueOpened}
					setOpened={setEditLangDialogueOpened}
					handleClose={handleEditedLangDialogueClose}
					index={indexLangEdited}
				/>
				<RenameDialogue
					opened={renameDialogueOpened}
					setOpened={setRenameDialogueOpened}
					handleClose={handleRenameDialogueClose}
					index={indexRenamed}
				/>
				<DeleteDialogue
					opened={deleteDialogueOpened}
					setOpened={setDeleteDialogueOpened}
					handleClose={handleDeleteDialogueClose}
					index={indexDeleted}
				/>
				<EditDictionariesDialogue
					opened={editDictsDialogueOpened}
					setOpened={setEditDictsDialogueOpened}
					handleClose={handleEditDictsDialogueClose}
					index={indexDictionariesEdited}
				/>
			</DragDropContext>
		);
	else
		return (
			<Typography
				variant='body'
			>
				{localisedStrings['generic-loading']}
			</Typography>
		);
}
