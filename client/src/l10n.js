import LocalizedStrings from 'react-localization';
import { RTL_LANGS } from './config';
import enGB from './translations/en-GB.json';
import enUS from './translations/en-US.json';
import zhCN from './translations/zh-CN.json';

export const localisedStrings = new LocalizedStrings({
	'en-GB': enGB,
	'en-US': enUS,
	'zh-CN': zhCN
});

export const interfaceLangIsRTL = RTL_LANGS.includes(localisedStrings.getLanguage());
