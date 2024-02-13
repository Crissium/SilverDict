import { interfaceLangIsRTL } from './l10n';

export const JSON_CONTENT_TYPE = 'application/json';

export const JSON_HEADER = {
	'Content-Type': JSON_CONTENT_TYPE
};

export function loadJson(response) {
	return response.json();
}

export const IS_DESKTOP_MEDIA_QUERY = '(min-width: 768px)';

export function dictionarySnake2Camel(dictionary) {
	return {
		displayName: dictionary.dictionary_display_name,
		name: dictionary.dictionary_name,
		format: dictionary.dictionary_format,
		filename: dictionary.dictionary_filename
	};
}

export function dictionaryCamel2Snake(dictionary) {
	return {
		dictionary_display_name: dictionary.displayName,
		dictionary_name: dictionary.name,
		dictionary_format: dictionary.format,
		dictionary_filename: dictionary.filename
	};
}

export function storePersistent(key, value) {
	try {
		if (value && value.length > 0 && value !== '""' && value !== '{}') { // empty string or empty object
			localStorage.setItem(key, value);
		}
	} catch (error) {
		alert(`Failed to store persistent data ${key}. Error: ${error}`);
	}
}

export function loadPersistent(key, defaultValue) {
	try {
		const value = localStorage.getItem(key);
		if (value !== null) {
			return value;
		} else {
			return defaultValue;
		}
	} catch (error) {
		alert(`Failed to load persistent data ${key}. Error: ${error}`);
	}
}

export function getSetFromLangString(lang) {
	lang = lang.replace(/\s/g, '');
	lang = lang.toLowerCase();
	const set = new Set();
	for (const l of lang.split(',')) {
		if (l.length > 0) {
			set.add(l);
		}
	}
	return set;
}

export function isRTL(s) {
	if (interfaceLangIsRTL) {
		return false; // RTL + RTL = weird RTL
	}

	var ltrChars =
		'A-Za-z\u00C0-\u00D6\u00D8-\u00F6\u00F8-\u02B8\u0300-\u0590\u0800-\u1FFF' +
		'\u2C00-\uFB1C\uFDFE-\uFE6F\uFEFD-\uFFFF';
	var rtlChars = '\u0591-\u07FF\uFB1D-\uFDFD\uFE70-\uFEFC';
	var rtlDirCheck = new RegExp('^[^' + ltrChars + ']*[' + rtlChars + ']');

	return rtlDirCheck.test(s);
}

export async function getElementByName(name) {
	return new Promise(function (resolve) {
		function getElement() {
			const element = document.getElementsByName(name)[0];
			if (element) {
				resolve(element);
			} else {
				requestAnimationFrame(getElement);
			}
		}
		getElement();
	});
}
