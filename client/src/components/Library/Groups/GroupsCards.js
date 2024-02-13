import React from 'react';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import Typography from '@mui/material/Typography';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import GroupCard from './GroupCard';
import { API_PREFIX } from '../../../config';
import { JSON_HEADER, loadJson } from '../../../utils';
import { useAppContext } from '../../../AppContext';
import { localisedStrings } from '../../../l10n';

export default function GroupsCards() {
	const { groups, setGroups } = useAppContext();

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

	if (groups)
		return (
			<DragDropContext onDragEnd={handleDrag}>
				<Droppable droppableId='groups'>
					{(provided) => (
						<List {...provided.droppableProps} ref={provided.innerRef}>
							{groups.map((g, index) => (
								<Draggable key={g.name} draggableId={g.name} index={index}>
									{(provided) => (
										<ListItem
											{...provided.draggableProps}
											{...provided.dragHandleProps}
											ref={provided.innerRef}
										>
											<GroupCard index={index} />
										</ListItem>
									)}
								</Draggable>
							))}
							{provided.placeholder}
						</List>
					)}
				</Droppable>
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
