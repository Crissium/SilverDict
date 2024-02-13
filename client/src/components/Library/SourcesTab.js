import React, { useState } from 'react';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import DeleteButton from '../common/DeleteButton';
import DeleteDialogue from './Sources/DeleteDialogue';
import { useAppContext } from '../../AppContext';

export default function SourcesTab() {
	const { sources } = useAppContext();
	const [indexToDelete, setIndexToDelete] = useState(-1);
	const [dialogueOpened, setDialogueOpened] = useState(false);

	function handleDialogueOpen(index) {
		setIndexToDelete(index);
		setDialogueOpened(true);
	}

	function handleDialogueClose() {
		setIndexToDelete(-1);
	}

	return (
		<>
			<Box height={1} overflow='scroll'>
				<List>
					{sources.map((source, index) => (
						<ListItem
							key={index}
							secondaryAction={
								<DeleteButton
									handleClick={() => handleDialogueOpen(index)}
								/>
							}
						>
							<ListItemText
								primary={source}
								primaryTypographyProps={{
									fontFamily: 'monospace'
								}}
							/>
						</ListItem>
					))}
				</List>
			</Box>
			<DeleteDialogue
				opened={dialogueOpened}
				setOpened={setDialogueOpened}
				handleClose={handleDialogueClose}
				index={indexToDelete}
			/>
		</>
	);
}
