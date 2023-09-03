# SilverDict – Web-Based Alternative to GoldenDict

![favicon](/client/public/favicon.ico)

This project is intended to be a modern, from-the-ground-up, maintainable alternative to [GoldenDict](https://github.com/goldendict/goldendict)(-[ng](https://github.com/xiaoyifang/goldendict-ng)), developed with Flask and Vue.js.

You can access the live demo [here](https://reverse-proxy-crissium.cloud.okteto.net/) (the button to delete dictionaries is removed). It lives inside a free Okteto container, which sleeps after 24 hours of inactivity, so please bear with its slowness and refresh the page a few times if you are seeing a 404 error, and remember that it may be out of sync with the latest code changes.

A note for users in China: Okteto 用的是 GCP, 在有些地方撞墙了。（如果你知道国内有免费的 Docker 容器服务，欢迎告诉我。）

## Screenshots

![Light (default)](/screenshots/light.png)
![Dark](/screenshots/dark.png)

The dark theme is not built in, but rendered with the [Dark Reader Firefox extension](https://addons.mozilla.org/en-GB/firefox/addon/darkreader/).

### Some Peculiarities

- The buttons in the right sidebar are _toggle buttons_.
- The wildcard characters are `^` and `+` (instead of `%` and `_` of SQL or the more traditional `*` and `?`) for technical reasons. Hint: imagine `%` and `_` are shifted one key to the right on an American keyboard.
- If you have accidentally cleared the history, you can restore it by refreshing the page.
- This project extracts resources from MDict dictionaries in advance. Therefore, if you are deploying to a server and have a local back-up, you can save space by adding to [silverdict.py](/server/app/silverdict.py):15 an argument `remove_resources_after_extraction=True`.
- This project overhauls[^3] DSL dictionaries and _silently overwrites_ the original files. I myself have tested with all my DSL dictionaries, but if you are unsure, back up your dictionaries first.
- During the indexing process of DSL dictionaries, the memory usage could reach as high as 1.5 GiB (tested with the largest DSL ever seen, the _Encyclopædia Britannica_), and even after that the memory used remains at around 500 MiB. Restart the server process and the memory usage will drop to a few MiB.

## Features

- Python[^1]-powered
- Cleaner code, in an un-Flasky way
- Deployable both locally and on a self-hosted server
- Fast enough (faster than my GoldenDict-ng compiled with Qt 5)
- Minimalist Vue-based frontend
- Separable client and server components

## Roadmap

- [ ] Linux: RPM/Deb packaging (will do when the project is more mature)
- [ ] Windows: package everything into a single click-to-run executable (will do when the project is more mature)

### Server-side

- [ ] Make the project more Flasky[^5]
- [ ] Add support for Babylon BGL glossary format (help wanted!)
- [X] Add support for StarDict format
- [X] Add support for ABBYY Lingvo DSL format[^4]
- [ ] ~~Rewrite the MDict reader class~~
- [ ] Inline styles to prevent them from being applied to the whole page (The commented-out implementation in `mdict_reader.py` breaks richly-formatted dictionaries.)
- [ ] **Reorganise APIs (to facilitate dictionary groups)**
- [X] Ignore diacritics when searching (testing still wanted from speakers of Turkish, the Semitic languages and Asian languages other than CJK)
- [X] Ignore case when searching
- [ ] GoldenDict-like morphology-awareness (walks -> walk) and spelling check (fuzzy-search, that is, malarky -> malady, Malaya, malarkey, Malay, Mala, Maalox, Malcolm)
- [X] Add the ability to set sources for automatic indexing, i.e. dictionaries put into the specified directories will be automatically added

Morphology dictionaries would require the user to specify the language, so we need add a new 'language(s)' field to the dictionary group metadata.

### Client-side

- [ ] Offer readily built static files for users unversed in the front-end development process (Artefacts built with GitHub Actions are only visible to me and the URL is not permanent)
- [ ] Refactor and clean up Vue code (help wanted!)
- [ ] Add proper styling for `<sound>` tags
- [X] Allow zooming in/out of the definition area
- [ ] Make the strings translatable (there are only a few of them, though)
- [ ] GoldenDict-like dictionary group support
- [ ] ~~Better support for mobile screens (help wanted!)~~ I am working on a mobile app

I would like to imitate GoldenDict Android's interface, where the input area is always at the top, and next to it is a button to select dictionaries; when the input is blank, history is displayed instead of matched candidates. I wonder where to put the miscellaneous buttons like the ones for clearing history and managing dictionaries.

## Usage

### Dependencies

This project utilises some Python 3.10 features, such as the _match_ syntax, and a minimal set of dependencies:
```
Flask
Flask-Cors
waitress
lxml
```

### Local Deployment

The simplest method to use this app is to run it locally. I would recommend running the custom HTTP server in the `http_server` sub-directory, which forwards requests under `/api` to the back-end, and serves static files in `./dist/`.

```bash
cd client
yarn install
yarn build
mv dist ../http_server/
```
And then:
```bash
pip3.10 install -r http_server/requirements.txt # or install with your system package manager
python3.10 http_server/http_server.py # working-directory-agnostic
pip3.10 install -r server/requirements.txt
python3.10 server/server.py # working-directory-agnostic
```

Then access it at [localhost:8081](http://localhost:8081). Please note that the favicon may be missing.

Alternatively, you could use dedicated HTTP servers such as nginx to serve the static files and proxy API requests. Check out the sample [config](/nginx.conf) for more information.


### Server Deployment

I recommend nginx if you plan to deploy SilverDict to a server. Before building the static files, be sure to modify `SERVER_URL` in `App.vue`, and then place them into whatever directory where nginx looks for static files. Remember to reverse-proxy all API requests and permit methods other than `GET` and `POST`.

Assuming your distribution uses systemd, you can refer to the provided sample systemd [config](/silverdict.service) and run the script as a service.

NB: currently the server is memory-inefficient: running the server with eight mid- to large-sized MDict dictionaries consumes ~200 MiB of memory, which is much higher than GoldenDict. There's no plan to fix this in the near future.[^2] If you want an MDict server with low memory footprint, take a look at xiaoyifang/goldendict-ng#229 and subscribe to [its RSS feed](https://rsshub.app/github/comments/xiaoyifang/goldendict-ng/229). A possible work-around: ditch MDict. Convert to other formats with pyglossary (might not work). There are no such issues with StarDict or DSL.

### Docker Deployment

Check out my [guide](https://crissium.github.io/posts/Docker/).

## Acknowledgements

The favicon is the icon for 'Dictionary' from the [Papirus icon theme](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme), licensed under GPLv3.

This project uses or has adapted code from the following projects:

| **Name** | **Developer** | **Licence** |
|:---:|:---:|:---:|
| [mdict-analysis](https://bitbucket.org/xwang/mdict-analysis/src/master/) | Xiaoqiang Wang |  |
| [python-stardict](https://github.com/pysuxing/python-stardict) | Su Xing | GPLv3 |
| dictionary-db | [Jean-François Dockes](mailto:jf@dockes.org) | GPL 2.1 |
| [idzip](https://github.com/fidlej/idzip) | Ivo Danihelka |  |
| [pyglossary](https://github.com/ilius/pyglossary) | Saeed Rasooli | GPLv3 |

## Similar projects

- [flask-mdict](https://github.com/liuyug/flask-mdict): this MDict-only project is broadly similar to mine, but adopts a more GoldenDict-like interface (where definitions of the same entry from different dictionaries are compiled into a single page, which I will switch to soon.), and uses an older version of Flask.

---

[^3]: What it does: (1) decompress the dictionary file if compressed; (2) remove the BOM, non-printing characters and strange symbols (only `{·}` currently) from the text; (3) normalize the initial whitespace characters of definition lines; (4) overwrite the `.dsl` file with UTF-8 encoding and re-compress with _dictzip_. After this process the file is smaller and easier to work with.

[^1]: A note about type hinting in the code: I know for proper type hinting I should use the module `typing`, but the current way is a little easier to write and can be understood by VS Code.

[^4]: I tested with an extremely ill-formed DSL dictionary, and before such devilry my cleaning code is powerless. I will look into how GoldenDict handles this.

[^2]: I grabbed a profiler and found the root of the cause: the MDict library stores many things in memory, so it is impossible for me to fix this without rewriting the library. Besides, I cannot instantiate `MDX` lazily, or the waiting time would easily get well beyond half a second.

[^5]: SilverDict is not a thin layer between the browser and the database, and in order to ease the development process, I have made some decisions that may be considered very strange by you Flask veterans out there. For example, I have written a custom database manager and a huge Config class that even has some getters and setters. What's more, I have subclassed `Flask` to store literally everything in this object instead of `g`, for which I have to define all APIs in the constructor instead of a blueprint. Now this project seems impossible to refactor into a more Flasky style as it grows ever larger. In a word, I have abandoned all the conveniences and programming styles of Flask and use it as a mere base server that has been extended grotesquely. If you have any suggestions concerning the organisation of the project, do create an issue and share your thoughts.\
_Dear reader, if you have waded through this drivel without scrolling away, here's more._ In fact I think it is possible to ditch Flask entirely and use Python's built-in HTTP server as the base, but that way the APIs would be much harder to write and I have to do multithreading myself.\
During my internship last summer I designed a three-part data analysis app. The first part fetches raw data every day, does all the hefty calculations and stores the results in a MariaDB database. The second part is a long-running Flask-based web server that basically serves as a middleware and stores little state in memory itself. When I said 'Flask-based' I meant a fully idiomatic Flask app with blueprints, SQLAlchemy and all that. The third part is a React web app divided into components, which fetches data from the second part and presents them nicely. I've got barely any mentorship during that, and I am not sure if it is a good design. Anyway it is easy to apply to SilverDict: the first part preprocesses dictionaries and stores clean HTML articles instead of indexes in the database; the second part is a very small Flask app that accepts requests, forwards them to the first part if applicable (e.g. dictionary/history management), and responds with the requested data; the third part is the current single-component Vue app. The only drawback to this scheme is that all the uncompressed HTML articles have to be stored in the database, which is not very efficient. But storage is cheap…\
