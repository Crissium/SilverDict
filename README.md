# SilverDict – Web-Based Alternative to GoldenDict

[![Crowdin](https://badges.crowdin.net/silverdict/localized.svg)](https://crowdin.com/project/silverdict)

[Documentation and Guides](https://github.com/Crissium/SilverDict/wiki) (Please read at least the general notes before using.)

This project is intended to be a modern, from-the-ground-up, maintainable alternative to [GoldenDict](https://github.com/goldendict/goldendict)(-[ng](https://github.com/xiaoyifang/goldendict-ng)), developed with Flask and React.

You can access the live demo [here](https://mathsdodger.eu.pythonanywhere.com/) (library management and settings are disabled). It is hosted by a free service so please bear with its slowness. Demo last updated on 13th February 2024.

## Screenshots

![Light 1](/docs/img/light1.png)
![Light 2](/docs/img/light2.png)
![Dark](/docs/img/dark.png)
![Mobile](/docs/img/mobile.png)

The dark theme is not built in, but rendered with the [Dark Reader Firefox extension](https://addons.mozilla.org/en-GB/firefox/addon/darkreader/).

_The new UI, as seen in the screenshots, hasn't been released yet._

### Some Peculiarities

- The wildcard characters are `^` and `+` (instead of `%` and `_` of SQL or the more traditional `*` and `?`) for technical reasons. Hint: imagine `%` and `_` are shifted one key to the right on an American keyboard.
- This project creates a back-up of DSL dictionaries, overhauls[^1] them and _silently overwrites_ the original files. So after adding a DSL dictionary to SilverDict, it may no longer work with GoldenDict.
- During the indexing process of DSL dictionaries, the memory usage could reach as high as 1.5 GiB (tested with the largest DSL ever seen, the _Encyclopædia Britannica_), and even after that the memory used remains at around 500 MiB. Restart the server process and the memory usage will drop to a few MiB. (The base server with no dictionaries loaded uses around 50 MiB of memory.)
- Both-sides suggestion matching is implemented with an $n$-gram based method, where $n = 4$, meaning that it will only begin working when the query is equal to or longer than 4 characters. This feature is disabled by default, and can be enabled by editing `~/.silverdict/preferences.yaml` and create the ngram table in the settings menu. This process could be slow. You have to do this manually each time a dictionary is added or deleted.

## Features

- Python-powered
- Cleaner code
- Deployable both locally and on a self-hosted server
- Fast enough
- Modern, clean and sleek web interface, with Material Design
- Works as expected
- DSL, StarDict, MDict supported
- Anki mode
- Cross-platform (Linux, Windows, MacOS, Android, limited iOS)

## Roadmap

- [ ] Linux: RPM/Deb packaging
- [ ] ?? Publish on PyPI
- [ ] Windows: package everything into a single click-to-run executable (help wanted)

### Server-side

- [ ] ~~Add support for Babylon BGL glossary format~~[^5]
- [X] Add support for StarDict format
- [X] Add support for ABBYY Lingvo DSL format
- [X] Reduce DSL parsing time
- [X] Reduce the memory footprint of the MDict Reader
- [ ] Inline styles to prevent them from being applied to the whole page (The commented-out implementation in [`server/app/dicts/mdict/html_cleaner.py`](/server/app/dicts/mdict/html_cleaner.py) breaks richly-formatted dictionaries.)[^2]
- [X] Reorganise APIs (to facilitate dictionary groups)
- [X] Ignore diacritics when searching (testing still wanted from speakers of Turkish and Asian languages other than CJK)
- [X] Ignore case when searching
- [X] GoldenDict-like morphology-awareness (walks -> walk) and spelling check (fuzzy-search, that is, malarky -> malady, Malaya, malarkey, Malay, Mala, Maalox, Malcolm)
- [X] Write [my own morphology analyser](https://github.com/Crissium/sibel) (Hunspell doesn't exactly meet the requirements of this project)
- [ ] Transliteration for the Cyrillic[^3], Greek, Arabic, Hebrew and Devanagari scripts (done: Greek, one-way Arabic)
- [X] OpenCC Chinese conversion (please set your preference in `~/.silverdict/preferences.yaml` and add `zh` to the group with Chinese dictionaries)
- [X] Add the ability to set sources for automatic indexing, i.e. dictionaries put into the specified directories will be automatically added
- [X] Recursive source scanning
- [X] Multithreaded article extraction (This project will benefit hugely from [no-GIL python](https://peps.python.org/pep-0703/))
- [X] Improve the performance of suggestions matching
- [X] Make the suggestion size customisable
- [X] Allow configure suggestion matching mode, listening address, running mode, etc. via a configuration file, without modifying code
- [X] Add a timestamp field to suggestions to avoid newer suggestions being overridden by older ones
- [X] Full-text search
- [X] Allow custom transformation scripts

### Client-side

- [X] Move from create-react-app to Vite
- [X] Allow zooming in/out of the definition area
- [X] Click to search for words in the definition
- [X] Localisation
- [X] GoldenDict-like dictionary group support
- [X] A mobile-friendly interface (retouch needed)
- [X] [A real mobile app](https://github.com/Crissium/SilverDict-mobile)
- [ ] A C++/Qt (or QML) desktop app[^4]

## Usage

### Dependencies

This project utilises some Python 3.10 features, such as the _match_ syntax, and a minimal set of dependencies:
```
PyYAML # for better efficiency, please install libyaml before building the wheel
Flask # the web framework
Flask-Cors
waitress # the WSGI server
python-idzip # for dictzip
python-lzo # for v1/v2 MDict
xxhash # for v3 MDict
dsl2html # for DSL
xdxf2html # for XDXF-formatted StarDicts
requests # for auto-update
```

The packages [`dsl2html`](https://github.com/Crissium/python-dsl) and [`xdxf2html`](https://github.com/Crissium/python-xdxf2html) are mine, and could potentially be used by other projects.

In order to enable the feature of morphology analysis, you need to place the Hunspell dictionaries into `~/.silverdict/hunspell`, and install the Python package `sibel` or `hunspell`. I developed [`sibel`](https://github.com/Crissium/sibel) as a faster alternative to PyHunspell. But installation is tricky (see its Readme) and currently the packaged Python environment for Windows (see below) only includes PyHunspell, as I don't have access to a Windows machine with MSVC at the moment. If you know how to compile things on Windows and would like to help, please file an issue or contact me by e-mail. As a side note, if your program also uses PyHunspell, try out Sibel, which I guarantee is much sweeter than the Hun.

In order to enable the feature of Chinese conversion, you need to install the Python package `opencc`.

To use full-text search, please install `xapian`, optionally also `lxml`. The exact usage is still to be documented.

#### Note about the non pure Python dependencies

`python-lzo`, `xxhash`, `dsl2html`, `xdxf2html` all have pure Python alternatives, but they are either much slower or not very robust. If you are unable to install `python-lzo` or `dsl2html`, no action is needed. For `xxhash`, please install the pure Python implementation `ppxxh` instead. For `xdxf2html`, install `lxml`, which is not pure Python either, but its binary wheels are available for most platforms.

### Local Deployment

The simplest method to use this app is to run it locally.

```bash
cd client
yarn install
yarn build
mv build ../server/
```
And then:
```bash
cd ../server
pip3.10 install -r requirements.txt
python3.10 server.py # working-directory-agnostic
```

Then access it at [localhost:2628](http://localhost:2628).

Or, if you do not wish to build the web app yourself or clone the whole repository, you can download from [release](https://github.com/Crissium/SilverDict/releases) a zip archive, which contains everything you need to run SilverDict.

For Windows users: A zip archive complete with a Python interpreter and all the dependencies is available in [release](https://github.com/Crissium/SilverDict/releases). Download the archive, unzip it, and double-click `setup.bat` to generate a shortcut. Then you can move it wherever you wish and click on it to run SilverDict. After launching the server, you can access it at [localhost:2628](http://localhost:2628).

For Termux users: run the bash script `termux_setup.sh` in the top-level directory, which will install all the dependencies, including hunspell. The script assumes you have enabled external storage access and will create a default source directory at `/sdcard/Documents/Dictionaries`.

Alternatively, you could use dedicated HTTP servers such as nginx to serve the static files and proxy API requests. Check out the sample [config](/nginx.conf) for more information.

### Server Deployment

I recommend nginx if you plan to deploy SilverDict to a server. Run `yarn build` to generate the static files of the web app, or download a prebuilt one from release (inside `server/build`), and then place them into whatever directory where nginx looks for static files. Remember to reverse-proxy all API requests and permit methods other than `GET` and `POST`.

Assuming your distribution uses systemd, you can refer to the provided sample systemd [config](/silverdict.service) and run the script as a service.

### ~~Docker Deployment~~

Docker is not recommended as you have to tuck in all your dictionary and, highly fragmented data files, which is not very practical. It is fine if you only run SilverDict locally, though.

## Contributing

- Start with an item in the roadmap, or open an issue to discuss your ideas. Please notify me if you are working on something to avoid duplicated efforts. I myself dislike enforcing a coding style, but please use descriptive, verbose variable names and UTF-8 encoding, LF line endings, and indent with tabs.
- Help me with the transliteration feature.
- Translate the guides into your language. You could edit them directly on GitHub.

## Acknowledgements

The favicon is the icon for 'Dictionary' from the [Papirus icon theme](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme), licensed under GPLv3.

This project uses or has adapted code from the following projects:

| **Name** | **Developer** | **Licence** |
|:---:|:---:|:---:|
| [mdict-analysis](https://bitbucket.org/xwang/mdict-analysis/src/master/) | Xiaoqiang Wang | GPLv3 |
| [mdict-query](https://github.com/mmjang/mdict-query) | mmjang | No licence |
| [python-stardict](https://github.com/pysuxing/python-stardict) | Su Xing | GPLv3 |
| dictionary-db (together with the $n$-gram method) | Jean-François Dockes | GPL 2.1 |
| [pyglossary](https://github.com/ilius/pyglossary) | Saeed Rasooli | GPLv3 |

I would also express my gratitude to Jiang Qian for his suggestions, encouragement and great help.

## Similar projects

- [flask-mdict](https://github.com/liuyug/flask-mdict)
- [GoldenDict-ng's proposed HTTP server](https://github.com/xiaoyifang/goldendict-ng/issues/229)
- [Lectus](https://codeberg.org/proteusx/Lectus)
- [django-mdict](https://github.com/jiangnianshun/django-mdict)
- [An ancient issue of GoldenDict](https://github.com/goldendict/goldendict/issues/618)
---

[^1]: What it does: (1) decompress the dictionary file if compressed; (2) remove the BOM, non-printing characters and strange symbols (only `{·}` currently) from the text; (3) normalize the initial whitespace characters of definition lines; (4) overwrite the `.dsl` file with UTF-8 encoding and re-compress with _dictzip_. After this process the file is smaller and easier to work with.

[^2]: The use of a custom styling manager such as Dark Reader is recommended until I fix this, as styles for different dictionaries interfere with each other. Or better, if you know CSS, you could just edit the dictionaries' stylesheets to make them less intrusive and individualistic.

[^3]: A Russian-speaking friend told me that it is unusual to type Russian on an American keyboard, so whether this feature is useful is open to doubt.

[^4]: I have come up with a name: _Kilvert_ (yeah, after the Welsh priest for its close resemblance to _SilverDict_, and the initial letter, of course, stands for KDE). (I'm on Xfce by the way.)

[^5]: GoldenDict stores the decoded entries and _full-text_ definitions in its custom index. I see no reason why I should follow suit when one can always convert dictionaries in this obnoxious format into HTML-formatted StarDict with the excellent [pyglossary](https://github.com/ilius/pyglossary).
