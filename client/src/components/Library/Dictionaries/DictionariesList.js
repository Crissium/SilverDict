import React, { useState } from 'react';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemSecondaryAction from '@mui/material/ListItemSecondaryAction';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import EditButton from '../../common/EditButton';
import RenameDictionaryDialogue from './RenameDictionaryDialogue';
import DeleteButton from '../../common/DeleteButton';
import DeleteDictionaryDialogue from './DeleteDictionaryDialogue';
import { API_PREFIX } from '../../../config';
import { JSON_HEADER, dictionarySnake2Camel, dictionaryCamel2Snake, loadJson } from '../../../utils';
import { useAppContext } from '../../../AppContext';
import { localisedStrings } from '../../../l10n';

export default function DictionariesList() {
	const { dictionaries, setDictionaries } = useAppContext();
	const [renameDialogueOpened, setRenameDialogueOpened] = useState(false);
	const [renamedDictionaryIndex, setRenamedDictionaryIndex] = useState(-1);
	const [deleteDialogueOpened, setDeleteDialogueOpened] = useState(false);
	const [toBeDeletedIndex, setToBeDeletedIndex] = useState(-1);

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
				<Droppable droppableId='dictionaries'>
					{(provided) => (
						<List {...provided.droppableProps} ref={provided.innerRef}>
							{dictionaries.map((d, index) => (
								<Draggable key={d.name} draggableId={d.name} index={index}>
									{(provided) => (
										<ListItem
											{...provided.draggableProps}
											{...provided.dragHandleProps}
											ref={provided.innerRef}
										>
											<ListItemText primary={d.displayName} />
											<ListItemSecondaryAction>
												<EditButton
													handleClick={() => handleRenameDialogueOpen(index)}
												/>
												<DeleteButton
													handleClick={() => handleDeleteDialogueOpen(index)}
												/>
											</ListItemSecondaryAction>
										</ListItem>
									)}
								</Draggable>
							))}
							{provided.placeholder}
						</List>
					)}
				</Droppable>
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
