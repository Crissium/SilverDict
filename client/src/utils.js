export const JSON_CONTENT_TYPE = 'application/json';

export const JSON_HEADER = {
	'Content-Type': JSON_CONTENT_TYPE
};

export function loadDataFromJsonResponse(response) {
	return response.json();
}

export function convertDictionarySnakeCaseToCamelCase(dictionary) {
	return {
		displayName: dictionary.dictionary_display_name,
		name: dictionary.dictionary_name,
		format: dictionary.dictionary_format,
		filename: dictionary.dictionary_filename
	};
}

export function convertDictionaryCamelCaseToSnakeCase(dictionary) {
	return {
		dictionary_display_name: dictionary.displayName,
		dictionary_name: dictionary.name,
		dictionary_format: dictionary.format,
		dictionary_filename: dictionary.filename
	};
}

export function getSetFromLangString(lang) {
	lang = lang.replace(/\s/g, '');
	lang = lang.toLowerCase();
	const set = new Set();
	for (const l of lang.split(',')) {
		set.add(l);
	}
	return set;
}