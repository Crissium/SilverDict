import React, { useState } from 'react';
import Accordion from '@mui/material/Accordion';
import AccordionActions from '@mui/material/AccordionActions';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import Button from '@mui/material/Button';
import Card from '@mui/material/Card';
import CardHeader from '@mui/material/CardHeader';
import CardContent from '@mui/material/CardContent';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import Typography from '@mui/material/Typography';
import ISO6391 from 'iso-639-1';
import EditButton from '../../common/EditButton';
import DeleteButton from '../../common/DeleteButton';
import EditLanguageDialogue from './EditLanguageDialogue';
import RenameDialogue from './RenameDialogue';
import DeleteDialogue from './DeleteDialogue';
import EditDictionariesDialogue from './EditDictionariesDialogue';
import { useAppContext } from '../../../AppContext';
import { isRTL } from '../../../utils';
import { localisedStrings } from '../../../l10n';

function Item(props) {
	const { index, content } = props;

	return (
		<ListItem
			disablePadding
			key={index}
		>
			<ListItemText
				primary={content}
				primaryTypographyProps={{
					dir: isRTL(content) ? 'rtl' : 'ltr'
				}}
			/>
		</ListItem>
	);
}

export default function GroupCard(props) {
	const { index } = props;
	const { dictionaries, groups, groupings } = useAppContext();
	const thisGroup = groups[index];
	const [renameDialogueOpened, setRenameDialogueOpened] = useState(false);
	const [editLangDialogueOpened, setEditLangDialogueOpened] = useState(false);
	const [deleteDialogueOpened, setDeleteDialogueOpened] = useState(false);
	const [editDictsDialogueOpened, setEditDictsDialogueOpened] = useState(false);

	function namesDictsInGroup(index) {
		const names = groupings[thisGroup.name];
		const displayNames = [];
		for (const d of dictionaries) {
			if (names.includes(d.name)) {
				displayNames.push(d.displayName);
			}
		}
		return displayNames;
	}

	function namesLangsOfGroup(index) {
		return groups[index].lang.map(ISO6391.getNativeName);
	}

	if (thisGroup)
		return (
			<>
				<Card sx={{ width: 1 }}>
					<CardHeader
						title={thisGroup.name}
						action={
							thisGroup.name === 'Default Group' ? <></> :
								<>
									<EditButton
										handleClick={() => setRenameDialogueOpened(true)}
									/>
									<DeleteButton
										handleClick={() => setDeleteDialogueOpened(true)}
									/>
								</>
						}
					/>
					<CardContent>
						<Accordion>
							<AccordionSummary
								expandIcon={<ExpandMoreIcon />}
							>
								{localisedStrings['library-screen-add-group-dialogue-textfield-lang-label']}
							</AccordionSummary>
							<AccordionDetails>
								<List>
									{namesLangsOfGroup(index).map((name, index) => (
										<Item
											index={index}
											content={name}
										/>
									))}
								</List>
							</AccordionDetails>
							<AccordionActions>
								<Button
									onClick={() => setEditLangDialogueOpened(true)}
								>
									{localisedStrings['generic-edit']}
								</Button>
							</AccordionActions>
						</Accordion>
						<Accordion>
							<AccordionSummary
								expandIcon={<ExpandMoreIcon />}
							>
								{localisedStrings['library-screen-dictionaries-tab-title']}
							</AccordionSummary>
							<AccordionDetails>
								<List>
									{namesDictsInGroup(index).map((name, index) => (
										<Item
											index={index}
											content={name}
										/>
									))}
								</List>
							</AccordionDetails>
							<AccordionActions>
								<Button
									onClick={() => setEditDictsDialogueOpened(true)}
								>
									{localisedStrings['generic-edit']}
								</Button>
							</AccordionActions>
						</Accordion>
					</CardContent>
				</Card>
				<EditLanguageDialogue
					opened={editLangDialogueOpened}
					setOpened={setEditLangDialogueOpened}
					handleClose={() => {}}
					index={index}
				/>
				<RenameDialogue
					opened={renameDialogueOpened}
					setOpened={setRenameDialogueOpened}
					handleClose={() => {}}
					index={index}
				/>
				<DeleteDialogue
					opened={deleteDialogueOpened}
					setOpened={setDeleteDialogueOpened}
					handleClose={() => {}}
					index={index}
				/>
				<EditDictionariesDialogue
					opened={editDictsDialogueOpened}
					setOpened={setEditDictsDialogueOpened}
					handleClose={() => setEditDictsDialogueOpened(false)}
					index={index}
				/>
			</>
		);
	else
		return (
			<Card>
				<CardContent>
					<Typography
						variant='body'
					>
						{localisedStrings['generic-loading']}
					</Typography>
				</CardContent>
			</Card>
		);
}
