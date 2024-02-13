import React from 'react';
import Input from '@mui/material/Input';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useQueryContext } from './QueryContext';
import { localisedStrings } from '../../l10n';
import { IS_DESKTOP_MEDIA_QUERY } from '../../utils';

export default function QueryInput() {
	const { searchTerm, setSearchTerm, inputRef, setShowingArticleView } = useQueryContext();
	const isDesktop = useMediaQuery(IS_DESKTOP_MEDIA_QUERY);

	function handleSearchTermChange(e) {
		setSearchTerm(e.target.value);
	}

	function handleFocus(e) {
		e.target.select();
		setShowingArticleView(false, !isDesktop);
	}

	function handleClick() {
		// On click, give the input focus, because clicking on the input but not the text doesn't
		if (inputRef.current) {
			inputRef.current.focus();
		}
	}

	return (
		<Input
			style={{flexShrink: 1, flexGrow: 0, border: 'none'}}
			inputProps={{
				style: {
					color: 'inherit',
					border: 'none'
				},
				autoCapitalize: 'none',
				autoCorrect: 'off',
				dir: 'auto'
			}}
			autoComplete='off'
			autoFocus={isDesktop}
			fullWidth={true}
			inputRef={inputRef}
			onChange={handleSearchTermChange}
			onClick={handleClick}
			onFocus={handleFocus}
			placeholder={localisedStrings['search-placeholder']}
			value={searchTerm}
		/>
	);
}