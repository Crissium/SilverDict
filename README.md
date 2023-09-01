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

## Features

- Python[^1]-powered
- Cleaner code (well, sort of; anyway, I cannot understand much of GoldenDict's code)
- Deployable both locally and on a self-hosted server
- Fast enough (faster than my GoldenDict-ng compiled with Qt 5)
- Minimalist Vue-based frontend
- Separable client and server components

## Roadmap

- [ ] RPM/Deb packaging

### Server-side

- [ ] Add support for Babylon BGL glossary format (help wanted!)
- [X] Add support for StarDict format
- [ ] Add support for ABBYY Lingvo DSL format (working on this)
- [X] Rewrite the MDict reader class
- [ ] Inline styles to prevent them from being applied to the whole page (The commented-out implementation in `mdict_reader.py` breaks richly-formatted dictionaries.)
- [ ] Reorganise APIs
- [X] Ignore diacritics when searching
- [X] Ignore case when searching
- [ ] GoldenDict-like morphology support (walks -> walk) and spelling check (fuzzy-search, that is, malarky -> malady, Malaya, malarkey, Malay, Mala, Maalox, Malcolm)

Morphology dictionaries would require the user to specify the language, so we may need to add a new 'language(s)' field to the dictionary metadata.

### Client-side

- [ ] Refactor and clean up Vue code (help wanted!)
- [ ] Allow custom styles (for now you can use XStyle and DarkReader, for example)
- [ ] Add proper styling for `<sound>` tags
- [X] Allow zooming in/out of the definition area
- [ ] Make the strings translatable (there are only a few of them, though)
- [ ] ~~Better support for mobile screens (help wanted!)~~ I am working on a mobile app

I would like to imitate GoldenDict Android's interface, where the input area is always at the top, and next to it is a button to select dictionaries; when the input is blank, history is displayed instead of matched candidates. I wonder where to put the miscellaneous buttons like the ones for clearing history and managing dictionaries.

## Usage

### Dependencies

This project utilises some Python 3.10 features, such as the _match_ syntax, and a minimal set of dependencies:
```
Flask
Flask-Cors
waitress
```

### Local Deployment

The simplest method to use this app is to run it locally. I would recommend running the custom HTTP server in the `http_server` sub-directory, which forwards requests under `/api` to the backend, and serves static files in `./dist/`.

```bash
cd client
yarn install
yarn build
mv dist ../http_server/
```
And then:
```bash
python3.10 http_server.py # inside /http_server
python3.10 server/server.py
```

Then access it at [localhost:8081](http://localhost:8081). Please note that the favicon may be missing.

Alternatively, you could use dedicated HTTP servers such as nginx to serve the static files and proxy API requests. Check out the sample [config](/nginx.conf) for more information.


### Server Deployment

I recommend nginx if you plan to deploy SilverDict to a server. Before building the static files, be sure to modify `SERVER_URL` in `App.vue`, and then place them into whatever directory where nginx looks for static files. Remember to reverse-proxy all API requests and permit methods other than `GET` and `POST`.

Assuming your distribution uses systemd, you can refer to the provided sample systemd [config](/silverdict.service) and run the script as a service.

NB: currently the server is memory-inefficient: running the server with eight mid- to large-sized dictionaries consumes ~200 MB of memory, which is much higher than GoldenDict. There's no plan to fix this in the near future.[^2] If you want a server with low memory footprint, take a look at xiaoyifang/goldendict-ng#229 and subscribe to [its RSS feed](https://rsshub.app/github/comments/xiaoyifang/goldendict-ng/229).

### Docker Deployment

Check out my [guide](https://crissium.github.io/posts/Docker/).

## Acknowledgements

The favicon is the icon for 'Dictionary' from the [Papirus icon theme](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme), licensed under GPLv3.

This project uses the [Python MDict library](https://bitbucket.org/xwang/mdict-analysis/src/master/) developed by Xiaoqiang Wang.

## Similar projects

I had no idea of these similar projects in the course of development. So please take a look at them and choose your favourite:

- [flask-mdict](https://github.com/liuyug/flask-mdict): it is broadly similar to mine, but adopts a more GoldenDict-like interface (where definitions of the same entry from different dictionaries are compiled into a single page.), and uses an older version of Flask.
- [mdx-server](https://github.com/ninja33/mdx-server): only one dictionary is accessible at once.

Note that these projects only have the MDict format in mind, while I plan to support three additional common formats.

---

[^1]: A note about type hinting in the code: I know for proper type hinting I should use the module `typing`, but the current way is a little easier to write and can be understood by VS Code.

[^2]: I grabbed a profiler and found the root of the cause: the `mdict_reader` library stores many things in memory, so it is impossible for me to fix this without rewriting the library.