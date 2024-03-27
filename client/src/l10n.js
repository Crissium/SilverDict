import LocalizedStrings from 'react-localization';
import { RTL_LANGS } from './config';
import enGB from './translations/en-GB.json';
import enUS from './translations/en-US.json';
import ruRU from './translations/ru-RU.json';
import zhCN from './translations/zh-CN.json';

export const localisedStrings = new LocalizedStrings({
	'en-GB': enGB,
	'en-US': enUS,
	'ru-RU': ruRU,
	'zh-CN': zhCN
});

export const interfaceLangIsRTL = RTL_LANGS.includes(localisedStrings.getLanguage());
