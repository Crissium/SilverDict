# SilverDict – Web-Based Alternative to ~~GoldenDict~~ MDict

![favicon](/client/public/favicon.ico)

This project is intended to be a modern, from-the-ground-up, maintainable alternative to [GoldenDict](https://github.com/goldendict/goldendict)(-[ng](https://github.com/xiaoyifang/goldendict-ng)), developed with Flask and Vue.js.

~~You can access the live demo [here](https://www.eplscz1rvblma3qpwsxvrpo930wah.xyz). Please be polite and do not abuse it, as my knowledge of security is limited. I've also removed the button to delete dictionaries. It may be out of sync with the latest code changes.~~

The demo is down for now. I will bring it back online in August.

## Screenshots

![Light (default)](/screenshots/light.png)
![Dark](/screenshots/dark.png)

The dark theme is not built in, but rendered with the [Dark Reader Firefox extension](https://addons.mozilla.org/en-GB/firefox/addon/darkreader/).

_The buttons in the right sidebar are toggle buttons._

## Features

- Python-powered
- Cleaner code (well, sort of; anyway, I cannot understand much of GoldenDict's code)
- Deployable both locally and on a self-hosted server
- Fast enough (faster than my GoldenDict-ng compiled with Qt 5)
- Minimalist Vue-based frontend
- Separable client and server components

## Roadmap

- [ ] RPM/Deb packaging
- [ ] Docker support

### Server-side

- [ ] Add support for Babylon BGL glossary format (help wanted!)
- [ ] Add support for StarDict format (help wanted!)
- [ ] Add support for ABBYY Lingvo DSL format (help wanted!)
- [X] Rewrite the MDict reader class
- [ ] Inline styles to prevent them from being applied to the whole page (The commented-out implementation in `mdict_reader.py` breaks richly-formatted dictionaries.)
- [ ] Reorganise APIs
- [X] Ignore diacritics when searching
- [X] Ignore case when searching
- [ ] GoldenDict-like morphology support (walks -> walk) and spelling check (fuzzy-search, that is, malarky -> malady, Malaya, malarkey, Malay, Mala, Maalox, Malcolm)

StarDict and DSL dictionaries use [*dictzip*](https://github.com/cheusov/dictd) (`.dz`) to compress text files, allowing random access and on-the-fly decompression. Unfortunately, the inner workings of dictzip involving bitwise operations are not well understood.[^1] As for BGL, its organisation is completely opaque to me.

Morphology dictionaries would require the user to specify the language, so we may need to add a new 'language(s)' field to the dictionary metadata.

### Client-side

- [ ] Refactor and clean up Vue code (help wanted!)
- [ ] Allow custom styles (for now you can use XStyle and DarkReader, for example)
- [ ] Add proper styling for `<sound>` tags
- [X] Allow zooming in/out of the definition area
- [ ] Make the strings translatable (there are only a few of them, though)
- [ ] Better support for mobile screens (help wanted!)
- [ ] ~~Allow specifying the server's URL directly in the frontend~~ (bad idea)

I would like to imitate GoldenDict Android's interface, where the input area is always at the top, and next to it is a button to select dictionaries; when the input is blank, history is displayed instead of matched candidates. I wonder where to put the miscellaneous buttons like the ones for clearing history and managing dictionaries.

## Usage

### Dependencies

This project utilises some Python 3.10 features, such as the _match_ syntax, and a minimal set of dependencies:
```
flask
flask-cors
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
python3.10 http_server/http_server.py
python3.10 server/server.py
```

Then access it at [localhost:8081](http://localhost:8081). Please note that the favicon may be missing.

Alternatively, you could use dedicated HTTP servers such as nginx to serve the static files and proxy API requests. Check out the sample [config](/nginx.conf) for more information.


### Server Deployment

I recommend nginx if you plan to deploy SilverDict to a server. Before building the static files, be sure to modify `SERVER_URL` in `App.vue`, and then place them into whatever directory where nginx looks for static files. Remember to reverse-proxy all API requests and permit methods other than `GET` and `POST`.

Assuming your distribution uses systemd, you can refer to the provided sample systemd [config](/silverdict.service) and run the script as a service.

NB: currently the server is memory-inefficient due to the way `MDictReader` is designed. Running the server with eight mid- to large-sized dictionaries consumes ~160 MB of memory, which is much higher than GoldenDict. There's no plan to fix this in the near future.

## Acknowledgements

The favicon is the icon for 'Dictionary' from the [Papirus icon theme](https://github.com/PapirusDevelopmentTeam/papirus-icon-theme), licensed under GPLv3.

This project uses the [Python MDict library](https://bitbucket.org/xwang/mdict-analysis/src/master/) developed by Xiaoqiang Wang.

## Similar projects

I had no idea of these similar projects in the course of development. So please take a look at them and choose your favourite:

- [flask-mdict](https://github.com/liuyug/flask-mdict): it is broadly similar to mine, but adopts a more GoldenDict-like interface (where definitions of the same entry from different dictionaries are compiled into a single page.), and uses an older version of Flask.
- [mdx-server](https://github.com/ninja33/mdx-server): only one dictionary is accessible at once.

Note that these projects only have the MDict format in mind, while I plan to support three additional common formats.

---

[^1]: Actually I think I have figured it out by reading the source code and the accompanying manpage. It's fairly simple. First you've got to know the structure of a gzip archive (read this excellent exposition if you don't: [https://commandlinefanatic.com/cgi-bin/showarticle.cgi?article=art001](https://commandlinefanatic.com/cgi-bin/showarticle.cgi?article=art001)). One of the special optional fields of the gzip header contains information about the chunk length, the number of chunks, and the offsets of the chunks, so that if you only need a tiny portion, you do not have to decompress the whole archive. Anyway _dictzip_ has only about 700 lines of code. However, when I tried to apply this knowledge to actual dictionary formats, I was stuck again. _How on earth am I to know which chunk the headword I am looking for is in?_ So, I embarked upon a daunting quest: to read the source code of the venerable GoldenDict-ng, only to discover that it even introduced further complexities. I won't be working on this for months to come.
