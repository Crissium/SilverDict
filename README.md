# SilverDict – Web-Based Alternative to GoldenDict

[![Crowdin](https://badges.crowdin.net/silverdict/localized.svg)](https://crowdin.com/project/silverdict)

[Documentation and Guides](https://github.com/Crissium/SilverDict/wiki) (Please read at least the general notes before using. There are some important notices.)

This project is intended to be a modern, from-the-ground-up, maintainable alternative to [GoldenDict](https://github.com/goldendict/goldendict)(-[ng](https://github.com/xiaoyifang/goldendict-ng)), developed with Flask and React.

You can access the live demo [here](https://mathsdodger.eu.pythonanywhere.com/) (library management and settings are disabled). It is hosted by Python Anywhere on a free plan, so it might be quite slow. Demo last updated on 16th August 2024.

## Screenshots

![Light 1](/docs/img/light1.png)
![Light 2](/docs/img/light2.png)
![Dark](/docs/img/dark.png)
![Mobile](/docs/img/mobile.png)

The dark theme is not built in, but rendered with the [Dark Reader Firefox extension](https://addons.mozilla.org/en-GB/firefox/addon/darkreader/).

## Features

- Python-powered
- Deployable both locally and on a self-hosted server
- Fast enough
- Modern, clean and sleek web interface, with Material Design
- DSL, StarDict, MDict supported
- [Anki mode](https://github.com/Crissium/SilverDict/wiki/webui#right-column)
- Full-text search (available on Unix systems only)
- Cross-platform (Linux, Windows, MacOS, Android, limited iOS)

## Roadmap

- [ ] Linux: RPM/Deb packaging, including various dependencies like `idzip`

### Server-side

- [ ] ~~Add support for Babylon BGL glossary format~~[^1]
- [ ] ~~Transliteration for the Cyrillic, Greek, Arabic, Hebrew and Devanagari scripts~~ (perhaps switching the keyboard layout is a far better solution, anyway Greek is already supported[^2])
- [ ] Make concurrent code thread-safe to prepare for [no-GIL python](https://peps.python.org/pep-0703/)

### Client-side

- [X] Localisation
- [X] [A real mobile app](https://github.com/Crissium/SilverDict-mobile)
- [ ] Make the browser's back/forward buttons work (help needed. `useSearchParams()` doesn't work.)
- [ ] (Ongoing) A C++/Qt (or QML) desktop client for better integration with the system (e.g. Ctrl+C+C to look up a word)

Note: If all you need is this key combination, then perhaps `xbindkeys` suffices, which is quite huge though. Or you can use the following script:

```python
import pyperclip
import webbrowser
from pynput import keyboard
from urllib.parse import urlencode

server_address = 'http://localhost:2628/'
group = 'English'

class KeyListener:
	def __init__(self):
		self.ctrl_pressed = False
		self.c_pressed_once = False

	def on_press(self, key):
		try:
			if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
				self.ctrl_pressed = True
			elif key.char == 'c' and self.ctrl_pressed:
				if self.c_pressed_once:
					selection = pyperclip.paste()
					# Uncomment (and comment the line below) to use the full web UI
					# params = urlencode({'group': group, 'key': selection})
					# webbrowser.open_new_tab(server_address + '?' + params)

					webbrowser.open_new_tab(f'{server_address}api/query/{group}/{selection}')
					self.reset()
				else:
					self.c_pressed_once = True
			else:
				self.reset()
		except AttributeError:
			self.reset()

	def on_release(self, key):
		if key == keyboard.Key.esc:
			return False

	def reset(self):
		self.ctrl_pressed = False
		self.c_pressed_once = False

if __name__ == '__main__':
	listener = KeyListener()
	with keyboard.Listener(
			on_press=listener.on_press,
			on_release=listener.on_release
		) as listener:
		listener.join()
```

## Usage

### Dependencies

This project utilises some Python 3.10 features, such as the _match_ syntax, and a minimal set of dependencies:
```
PyYAML # configuration files
Flask # the web framework
Flask-Cors
waitress # the WSGI server, note: other servers like Gunicorn and uWSGI work but you have to adjust the code
python-idzip # for dictzip
python-lzo # for v1/v2 MDict
xxhash # for v3 MDict
dsl2html # for DSL
xdxf2html # for XDXF-formatted StarDicts
requests # for auto-update
```

The packages [`dsl2html`](https://github.com/Crissium/python-dsl) and [`xdxf2html`](https://github.com/Crissium/python-xdxf2html) are mine, and could potentially be used by other projects.

In order to enable morphology analysis, you need to place the Hunspell dictionaries into `~/.silverdict/hunspell`, and install the Python package `sibel` or `hunspell`. I developed [`sibel`](https://github.com/Crissium/sibel) as a faster alternative to PyHunspell. But it might be difficult to install (see its Readme).

In order to enable Simplified/Traditional Chinese conversion, you need to install the Python package `opencc`.

To use full-text search, please install `xapian` and the Python bindings, optionally also `lxml`.

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

### Docker Deployment

#### Build Docker Image from Source

```bash
docker build --tag silverdict https://github.com/Crissium/SilverDict.git
docker run --rm --publish 2628:2628 --volume ${PATH_TO_DICTIONARIES}:/root/.silverdict/ --name silverdict silverdict
```

`${PATH_TO_DICTIONARIES}` is the path where settings and dictionaries are stored. The default path to scan is `${PATH_TO_DICTIONARIES}/source` for dictionaries and `${PATH_TO_DICTIONARIES}/hunspell` for spellchecking libraries (if enabled).

When building the Docker image, optional features can be enabled by passing `--build-arg`. For example, if you want to enable full text search: 

```bash
docker build --tag silverdict --build-arg ENABLE_FULL_TEXT_SEARCH=true https://github.com/Crissium/SilverDict.git
```

Available arguments are:

| Argument                    | value              | default |
| --------------------------- | ------------------ | ------- |
| ENABLE_FULL_TEXT_SEARCH     | true or empty      | empty   |
| ENABLE_MORPHOLOGY_ANALYSIS  | true or empty      | empty   |
| ENABLE_CHINESE_CONVERSION   | true or empty      | empty   |

Or use Docker Compose: Edit `docker-compose.yml` and

```bash
docker compose up -d
```

Note that if the paths to be mounted do not exist, Docker will create them with root ownership.

#### Use Ready-Built Docker Image

```bash
docker pull mathdodger/silverdict
```

Then run the container as above. This image is built with all three optional features enabled.

## Contributing

- Start with an item in the roadmap, or open an issue to discuss your ideas. Please notify me if you are working on something to avoid duplicated efforts. I myself dislike enforcing a coding style, but please use descriptive, verbose variable names and UTF-8 encoding, LF line endings, and indent with tabs.
- Translate the guides into your language. You could edit them directly on GitHub or translate on Crowdin.
- Translate the web UI on [Crowdin](https://crowdin.com/project/silverdict/invite?h=1ae82ee0d45867272b3af80cc93779871997870). Please open an issue or send me a PM on Crowdin if your language's not there.

### Donations

#### International

- [GitHub Sponsors](https://github.com/sponsors/Crissium)
- [Liberapay](https://liberapay.com/mathsdodger)
- [PayPal](https://paypal.me/mathsdodger)
- Bank transfer
	- SWIFT BIC: BKCHHKHHXXX
	- Bank Name: BANK OF CHINA (HONG KONG) LIMITED, HONG KONG
	- Main Address: BANK OF CHINA TOWER, 1 GARDEN ROAD, CENTRAL, HONG KONG
	- Account Number:
		- 012-591-2-087111-3 (accepted currencies: RMB, USD, GBP, JPY, SGD, AUD, NZD, CAD, EUR, CHF, DKK, NOK, SEK, THB, BND, ZAR)
		- 012-591-2-087110-0 (accepts HKD only)
	- Name: XING YI

#### China

<div style="display: flex; gap: 16px;">
  <img src="docs/img/WeixinReward.png" alt="Weixin Reward Code" height="400"/>
  <img src="docs/img/Alipay.jpg" alt="Alipay" height="400"/>
</div>

#### Hong Kong

Please send to this account instead of the BOCHK one above:
- Bank Name: Mox Bank Limited
- Bank Code: 389
- Branch Code-Account Number: 749-77343172
- Name: YI XING

## Credits

The favicon is the icon for 'Dictionary' from the [Papirus icon theme](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme), licensed under GPLv3.

The Dockerfile is contributed by [simonmysun](https://github.com/simonmysun).

This project uses or has adapted code from the following projects:

| **Name** | **Developer** | **Licence** |
|:---:|:---:|:---:|
| [GoldenDict](https://github.com/goldendict/goldendict) | Konstantin Isakov | GPLv3 |
| [mdict-analysis](https://bitbucket.org/xwang/mdict-analysis/src/master/) | Xiaoqiang Wang | GPLv3 |
| [mdict-query](https://github.com/mmjang/mdict-query) | mmjang | No licence |
| [python-stardict](https://github.com/pysuxing/python-stardict) | Su Xing | GPLv3 |
| dictionary-db (together with the n-gram method) | Jean-François Dockes | GPL 2.1 |
| [pyglossary](https://github.com/ilius/pyglossary) | Saeed Rasooli | GPLv3 |

I would also express my gratitude to my long-time 'alpha-tester' Jiang Qian, without whom this project could never become what it is today.

## Similar projects

- [flask-mdict](https://github.com/liuyug/flask-mdict)
- [GoldenDict-ng's proposed HTTP server](https://github.com/xiaoyifang/goldendict-ng/issues/229)
- [Lectus](https://codeberg.org/proteusx/Lectus) (DSL only, in Perl)
- [django-mdict](https://github.com/jiangnianshun/django-mdict)
- [An ancient issue of GoldenDict](https://github.com/goldendict/goldendict/issues/618)

---

[^1]: GoldenDict stores the decoded entries and _full-text_ definitions in its custom index. I see no reason why I should follow suit when one can always convert dictionaries in this obnoxious format into HTML-formatted StarDict with the excellent [pyglossary](https://github.com/ilius/pyglossary).

[^2]: The original use case is to support an ancient Greek lexicon that uses mixed Greek/Beta Code headwords. Normal dictionaries should not have this problem. Besides, implementing, say, a QWERTY-JCUKEN mapping is too trivial, whereas real transliteration is overcomplicated.
