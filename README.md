# SilverDict – Web-Based Alternative to GoldenDict

![favicon](/client/public/favicon.ico)

[Documentation and Guides](https://github.com/Crissium/SilverDict/wiki)

This project is intended to be a modern, from-the-ground-up, maintainable alternative to [GoldenDict](https://github.com/goldendict/goldendict)(-[ng](https://github.com/xiaoyifang/goldendict-ng)), developed with Flask and React.

You can access the live demo [here](https://reverse-proxy-crissium.cloud.okteto.net/) (the button to delete dictionaries is removed). It lives inside a free Okteto container, which sleeps after 24 hours of inactivity, so please bear with its slowness and refresh the page a few times if you are seeing a 404 error, and remember that it may be (terribly) out of sync with the latest code changes.

## Screenshots

![Light 1](/screenshots/light1.png)
![Light 2](/screenshots/light2.png)
![Dark](/screenshots/dark.png)
![Mobile](/screenshots/mobile.png)

The dark theme is not built in, but rendered with the [Dark Reader Firefox extension](https://addons.mozilla.org/en-GB/firefox/addon/darkreader/).

### Some Peculiarities

- The wildcard characters are `^` and `+` (instead of `%` and `_` of SQL or the more traditional `*` and `?`) for technical reasons. Hint: imagine `%` and `_` are shifted one key to the right on an American keyboard.
- This project creates a back-up of DSL dictionaries, overhauls[^3] them and _silently overwrites_ the original files. So after adding a DSL dictionary to SilverDict, it may no longer work with GoldenDict.
- During the indexing process of DSL dictionaries, the memory usage could reach as high as 1.5 GiB (tested with the largest DSL ever seen, the _Encyclopædia Britannica_), and even after that the memory used remains at around 500 MiB. Restart the server process and the memory usage will drop to a few MiB. (The base server with no dictionaries loaded uses around 50 MiB of memory.)
- Both-sides suggestion matching is implemented with an $n$-gram based method, where $n = 4$, meaning that it will only begin working when the query is equal to or longer than 4 characters. This feature is disabled by default, and can be enabled by editing `~/.silverdict/preferences.yaml` and create the ngram table in the settings menu. This process could be slow. You have to do this manually each time a dictionary is added or deleted.

## Features

- Python[^1]-powered
- Cleaner code
- Deployable both locally and on a self-hosted server
- Fast enough
- Minimalist web interface
- Separable client and server components
- Works as expected
- Cross-platform (Linux, Windows, MacOS, Android, limited iOS)

## Roadmap

- [ ] Linux: RPM/Deb packaging
- [ ] ?? Publish on PyPI
- [ ] Windows: package everything into a single click-to-run executable (help wanted)

### Server-side

- [ ] Add support for Babylon BGL glossary format
- [X] Add support for StarDict format
- [X] Add support for ABBYY Lingvo DSL format[^4]
- [ ] Reduce DSL indexing and parsing time
- [X] Reduce the memory footprint of the MDict Reader
- [ ] Inline styles to prevent them from being applied to the whole page (The commented-out implementation in `mdict_reader.py` breaks richly-formatted dictionaries.)[^5]
- [X] Reorganise APIs (to facilitate dictionary groups)
- [X] Ignore diacritics when searching (testing still wanted from speakers of Turkish and Asian languages other than CJK)
- [X] Ignore case when searching
- [X] GoldenDict-like morphology-awareness (walks -> walk) and spelling check (fuzzy-search, that is, malarky -> malady, Malaya, malarkey, Malay, Mala, Maalox, Malcolm)
- [ ] Transliteration for the Cyrillic[^6], Greek, Arabic, Hebrew and Devanagari scripts (done: Greek, one-way Arabic)
- [X] OpenCC Chinese conversion (please set your preference in `~/.silverdict/preferences.yaml` and add `zh` to the group with Chinese dictionaries)
- [X] Add the ability to set sources for automatic indexing, i.e. dictionaries put into the specified directories will be automatically added
- [X] Recursive source scanning
- [X] Multithreaded article extraction
- [X] Improve the performance of suggestions matching
- [X] Make the suggestion size customisable
- [X] Allow configure suggestion matching mode, listening address, running mode, etc. via a configuration file, without modifying code
- [X] Add a timestamp field to suggestions to avoid newer suggestions being overridden by older ones
- [ ] Use a linter

### Client-side

- [ ] Use the Bootstrap framework
- [X] Allow zooming in/out of the definition area
- [X] Click to search for words in the definition
- [ ] Make the strings translatable
- [X] GoldenDict-like dictionary group support
- [X] A mobile-friendly interface (retouch needed)
- [ ] [A real mobile app](https://github.com/Crissium/SilverDict-mobile)
- [ ] A C++/Qt (or QML) desktop app (development is scheduled to begin in July, 2024)[^7]

### Issue backlog

- [ ] Malformed DSL tags
- [ ] Make the dialogues children of the root element (How can I do this with nested dialogues?)

## Usage

### Dependencies

This project utilises some Python 3.10 features, such as the _match_ syntax, and a minimal set of dependencies:
```
PyYAML # for better efficiency, please install libyaml before building the wheel
Flask
Flask-Cors
waitress
python-idzip
lxml
```

In order to enable the feature of morphology analysis, you need to install the Python package `hunspell` and place the Hunspell dictionaries into `~/.silverdict/hunspell`.

In order to enable the feature of Chinese conversion, you need to install the Python package `opencc`.

### Local Deployment

The simplest method to use this app is to run it locally. I would recommend running the custom HTTP server in the `http_server` sub-directory, which forwards requests under `/api` to the back-end, and serves static files in `./build/`.

```bash
cd client
yarn install
yarn build
mv build ../http_server/
```
And then:
```bash
pip3.10 install -r http_server/requirements.txt # or install with your system package manager
python3.10 http_server/http_server.py # working-directory-agnostic
pip3.10 install -r server/requirements.txt
python3.10 server/server.py # working-directory-agnostic
```

Then access it at [localhost:8081](http://localhost:8081).

Or, if you do not wish to build the web app yourself or clone the whole repository, you can download from [release](https://github.com/Crissium/SilverDict/releases) a zip archive, which contains everything you need to run SilverDict.

For Windows users: A zip archive complete with a Python interpreter and all the dependencies is available in [release](https://github.com/Crissium/SilverDict/releases). Download the archive, unzip it, and double-click `setup.bat` to generate the shortcuts. Then you can move them wherever you wish and click on them to run SilverDict. After launching the server, you can access it at [localhost:8081](http://localhost:8081).

For Termux users: run the bash script `termux_setup.sh` in the top-level directory, which will install all the dependencies, including hunspell. The script assumes you have enabled external storage access and will create a default source directory at `/sdcard/Documents/Dictionaries`.

Optional: inside /http_server/ run `python3.10 change_server_address.py` to make your front-end connect to the actual server if accessed from a different machine.

Alternatively, you could use dedicated HTTP servers such as nginx to serve the static files and proxy API requests. Check out the sample [config](/nginx.conf) for more information.

### Server Deployment

I recommend nginx if you plan to deploy SilverDict to a server. Before building the static files, be sure to modify `API_PREFIX` in [`config.js`](/client/src/config.js), and then place them into whatever directory where nginx looks for static files. Remember to reverse-proxy all API requests and permit methods other than `GET` and `POST`.

Assuming your distribution uses systemd, you can refer to the provided sample systemd [config](/silverdict.service) and run the script as a service.

### ~~Docker Deployment~~

Docker is not recommended as you have to tuck in all your dictionary and, highly fragmented data files, which is not very practical.

## Acknowledgements

The favicon is the icon for 'Dictionary' from the [Papirus icon theme](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme), licensed under GPLv3.

This project uses or has adapted code from the following projects:

| **Name** | **Developer** | **Licence** |
|:---:|:---:|:---:|
| [mdict-analysis](https://bitbucket.org/xwang/mdict-analysis/src/master/) | Xiaoqiang Wang | GPLv3 |
| [python-stardict](https://github.com/pysuxing/python-stardict) | Su Xing | GPLv3 |
| dictionary-db (together with the $n$-gram method) | Jean-François Dockes | GPL 2.1 |
| [pyglossary](https://github.com/ilius/pyglossary) | Saeed Rasooli | GPLv3 |

I would also express my gratitude to Jiang Qian for his suggestions, encouragement and great help.

## Similar projects

- [flask-mdict](https://github.com/liuyug/flask-mdict)
- [GoldenDict-ng's proposed HTTP server](https://github.com/xiaoyifang/goldendict-ng/issues/229)
- [Lectus](https://github.com/proteusx/lectus)
- [django-mdict](https://github.com/jiangnianshun/django-mdict)
- [An ancient issue of GoldenDict](https://github.com/goldendict/goldendict/issues/618)
---

[^3]: What it does: (1) decompress the dictionary file if compressed; (2) remove the BOM, non-printing characters and strange symbols (only `{·}` currently) from the text; (3) normalize the initial whitespace characters of definition lines; (4) overwrite the `.dsl` file with UTF-8 encoding and re-compress with _dictzip_. After this process the file is smaller and easier to work with.

[^1]: A note about type hinting in the code: I know for proper type hinting I should use the module `typing`, but the current way is a little easier to write and can be understood by VS Code.

[^4]: I tested with an extremely ill-formed DSL dictionary, and before such devilry my cleaning code is powerless. I will look into how GoldenDict handles this.

[^5]: The use of a custom styling manager such as Dark Reader is recommended until I fix this, as styles for different dictionaries meddle with each other.

[^6]: A Russian-speaking friend told me that it is unusual to type Russian on an American keyboard, so whether this feature is useful is open to doubt.

[^7]: I have come up with a name: _Kilvert_ (yeah, after the Welsh priest for its close resemblance to _SilverDict_, and the initial letter, of course, stands for KDE). (I'm on Xfce by the way.)