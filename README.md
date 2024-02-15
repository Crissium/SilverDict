# SilverDict – Web-Based Alternative to GoldenDict

[![Crowdin](https://badges.crowdin.net/silverdict/localized.svg)](https://crowdin.com/project/silverdict)

[Documentation and Guides](https://github.com/Crissium/SilverDict/wiki) (Please read at least the general notes before using. There are some important notices.)

This project is intended to be a modern, from-the-ground-up, maintainable alternative to [GoldenDict](https://github.com/goldendict/goldendict)(-[ng](https://github.com/xiaoyifang/goldendict-ng)), developed with Flask and React.

You can access the live demo [here](https://mathsdodger.eu.pythonanywhere.com/) (library management and settings are disabled). It is hosted by a free service so please bear with its slowness. Demo last updated on 13th February 2024.

## Screenshots

![Light 1](/docs/img/light1.png)
![Light 2](/docs/img/light2.png)
![Dark](/docs/img/dark.png)
![Mobile](/docs/img/mobile.png)

The dark theme is not built in, but rendered with the [Dark Reader Firefox extension](https://addons.mozilla.org/en-GB/firefox/addon/darkreader/).

## Features

- Python-powered
- Cleaner code
- Deployable both locally and on a self-hosted server
- Fast enough
- Modern, clean and sleek web interface, with Material Design
- Works as expected
- DSL, StarDict, MDict supported
- Anki mode
- Full-text search (available on Unix systems only)
- Cross-platform (Linux, Windows, MacOS, Android, limited iOS)

## Roadmap

- [ ] Linux: RPM/Deb packaging
- [ ] ?? Publish on PyPI
- [ ] Windows: package everything into a single click-to-run executable (help wanted)

### Server-side

- [ ] ~~Add support for Babylon BGL glossary format~~[^5]
- [ ] Inline styles to prevent them from being applied to the whole page (The commented-out implementation in [`server/app/dicts/mdict/html_cleaner.py`](/server/app/dicts/mdict/html_cleaner.py) breaks richly-formatted dictionaries.)[^2]
- [ ] Transliteration for the Cyrillic[^3], Greek, Arabic, Hebrew and Devanagari scripts (done: Greek, one-way Arabic, though only Arabic itself is supported at the moment, if you'd like to help with Farsi, Urdu, etc., please open an issue)
- [X] Add the ability to set sources for automatic indexing, i.e. dictionaries put into the specified directories will be automatically added
- [X] Recursive source scanning
- [ ] Lock list operations to prepare for [no-GIL python](https://peps.python.org/pep-0703/)

### Client-side

- [X] Localisation
- [X] [A real mobile app](https://github.com/Crissium/SilverDict-mobile)
- [ ] A C++/Qt (or QML) desktop app[^4]

## Usage

### Dependencies

This project utilises some Python 3.10 features, such as the _match_ syntax, and a minimal set of dependencies:
```
PyYAML # configuration files
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

In order to enable the feature of morphology analysis, you need to place the Hunspell dictionaries into `~/.silverdict/hunspell`, and install the Python package `sibel` or `hunspell`. I developed [`sibel`](https://github.com/Crissium/sibel) as a faster alternative to PyHunspell. But it could be tricky to install (see its Readme). As a side note, if your program also uses PyHunspell, try out Sibel, which I guarantee is much sweeter than the Hun.

In order to enable the feature of Chinese conversion, you need to install the Python package `opencc`.

To use full-text search, please install `xapian`, optionally also `lxml`.

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
pip install -r requirements.txt
python server.py # working-directory-agnostic
```

Then access it at [localhost:2628](http://localhost:2628).

Or, if you do not wish to build the web app yourself or clone the whole repository, you can download from [release](https://github.com/Crissium/SilverDict/releases) a zip archive, which contains everything you need to run SilverDict.

For Windows users: A zip archive complete with a Python interpreter and all the dependencies (except for Xapian) is available in [release](https://github.com/Crissium/SilverDict/releases). Download the archive, unzip it, and double-click `setup.bat` to generate a shortcut. Then you can move it wherever you wish and click on it to run SilverDict. After launching the server, you can access it at [localhost:2628](http://localhost:2628).

For Termux users: run the bash script `termux_setup.sh` in the top-level directory, which will install all the dependencies, including PyHunspell. The script assumes you have enabled external storage access and will create a default source directory at `/sdcard/Documents/Dictionaries`.

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
- Translate the web UI on [Crowdin](https://crowdin.com/project/silverdict/invite?h=1ae82ee0d45867272b3af80cc93779871997870). Please open an issue or send me a PM on Crowdin if your language's not there.

## Credits

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

- [flask-mdict](https://github.com/liuyug/flask-mdict) (MDict only, pure Python)
- [GoldenDict-ng's proposed HTTP server](https://github.com/xiaoyifang/goldendict-ng/issues/229) (stuck at the moment)
- [Lectus](https://codeberg.org/proteusx/Lectus) (DSL only, in Perl)
- [django-mdict](https://github.com/jiangnianshun/django-mdict) (MDict only, very fast)
- [An ancient issue of GoldenDict](https://github.com/goldendict/goldendict/issues/618)

---


[^2]: The use of a custom styling manager such as Dark Reader is recommended until I fix this, as styles for different dictionaries interfere with each other. Or better, if you know CSS, you could just edit the dictionaries' stylesheets to make them less intrusive and individualistic.

[^3]: A Russian-speaking friend told me that it is unusual to type Russian on an American keyboard, so whether this feature is useful is open to doubt.

[^4]: I have come up with a name: _Kilvert_ (yeah, after the Welsh priest for its close resemblance to _SilverDict_, and the initial letter, of course, stands for KDE). (I'm on Xfce by the way.)

[^5]: GoldenDict stores the decoded entries and _full-text_ definitions in its custom index. I see no reason why I should follow suit when one can always convert dictionaries in this obnoxious format into HTML-formatted StarDict with the excellent [pyglossary](https://github.com/ilius/pyglossary).
