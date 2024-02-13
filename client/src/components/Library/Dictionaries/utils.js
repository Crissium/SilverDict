import { API_PREFIX } from '../../../config';
import { loadJson, JSON_HEADER } from '../../../utils';
import { localisedStrings } from '../../../l10n';

export async function getHeadwordCount(dictName) {
	try {
		const response = await fetch(`${API_PREFIX}/management/headword_count`, {
			method: 'POST',
			headers: JSON_HEADER,
			body: JSON.stringify({name: dictName})
		});
		const data = await loadJson(response);
		return data.count;
	} catch (error) {
		alert(localisedStrings['failure-fetching-headword-count'] + '\n' + error);
		return 0;
	}
}
