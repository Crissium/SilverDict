import LocalizedStrings from 'react-localization';
import { RTL_LANGS } from './config';
import enGB from './translations/en-GB.json';

export const localisedStrings = new LocalizedStrings({
	'en-GB': enGB,
});

export const interfaceLangIsRTL = RTL_LANGS.includes(localisedStrings.getLanguage());
