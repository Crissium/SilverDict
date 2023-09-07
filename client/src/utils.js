import { parse } from "yaml";

export const YAML_CONTENT_TYPE = 'text/plain; charset=utf-8';

export const YAML_HEADER = {
	'Content-Type': YAML_CONTENT_TYPE
};

export async function loadDataFromYamlResponse(response) {
	const text = await response.text();
	return parse(text);
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