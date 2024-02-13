import React, { useRef } from 'react';
import Input from '@mui/material/Input';
import useMediaQuery from '@mui/material/useMediaQuery';
import { useFtsContext } from './FtsContext';
import { localisedStrings } from '../../l10n';
import { IS_DESKTOP_MEDIA_QUERY } from '../../utils';

export default function FtsInput() {
	const { searchTerm, setSearchTerm, search, scrollToTop } = useFtsContext();
	const isDesktop = useMediaQuery(IS_DESKTOP_MEDIA_QUERY);
	const inputRef = useRef(null);

	function handleSearchTermChange(e) {
		setSearchTerm(e.target.value);
	}

	function handleFocus(e) {
		e.target.select();
	}

	function handleClick() {
		// On click, give the input focus, because clicking on the input but not the text doesn't
		if (inputRef.current) {
			inputRef.current.focus();
		}
	}

	function handleKeyDown(e) {
		if (e.key === 'Enter') {
			e.preventDefault();
			search(searchTerm);
			scrollToTop();
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
			onKeyDown={handleKeyDown}
			placeholder={localisedStrings['full-text-search-placeholder']}
			value={searchTerm}
		/>
	);
}