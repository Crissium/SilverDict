# SilverDict – Web-Based Alternative to ~~GoldenDict~~ MDict

![favicon](/client/public/favicon.ico)

This project is intended to be a modern, from-the-ground-up, maintainable alternative to [GoldenDict](https://github.com/goldendict/goldendict)(-[ng](https://github.com/xiaoyifang/goldendict-ng)), written with Flask and Vue.js.

You can access the live demo [here](https://www.eplscz1rvblma3qpwsxvrpo930wah.xyz). (Please be polite and do not abuse it, as my knowledge of security is limited. And I've removed the button to delete dictionaries.)

## Screenshots

![Light (default)](/screenshots/light.png)
![Dark](/screenshots/dark.png)

The dark theme is not built in, but rendered with the [DarkReader Firefox extension](https://addons.mozilla.org/en-GB/firefox/addon/darkreader/).

## Features

- Python-powered
- Cleaner code (well, sort of; anyway, I cannot understand much of GoldenDict's code)
- Deployable both locally and on a self-hosted server
- Fast enough (faster than my GoldenDict compiled with Qt 5)
- Minimalist Vue-based frontend
- Separable client and server components

## Roadmap

- [ ] RPM/Deb packaging
- [ ] Docker support

### Server-side

- [ ] Add support for Babylon BGL glossary format (help wanted!)
- [ ] Add support for StarDict format (help wanted!)
- [ ] Add support for ABBYY Lingvo DSL format (help wanted!)
- [ ] Rewrite the MDict reader class
- [ ] Reorganise APIs
- [X] Ignore diacritics when searching
- [X] Ignore case when searching
- [ ] GoldenDict-like morphology support (walks -> walk) and spelling check (fuzzy-search, that is, malarky -> malady, Malaya, malarkey, Malay, Mala, Maalox, Malcolm)

StarDict and DSL dictionaries use [`dictzip`](https://github.com/cheusov/dictd) (`.dz`) to compress text files, allowing random access and on-the-fly decompression. Unfortunately, the inner workings of dictzip involving bitwise operations are not well understood. As for BGL, its organisation is completely opaque to me.

This project uses the [Python MDict library](https://bitbucket.org/xwang/mdict-analysis/src/master/) developed by Xiaoqiang Wang. It is not designed for lookups, though, so I should have adapted it specifically for this project instead of directly using it as a base reader.

Morphology dictionaries would require the user to specify the language, so we may need to add a new 'language(s)' field to the dictionary metadata.

### Client-side

- [ ] Refactor and clean up Vue code (help wanted!)
- [ ] Allow custom styles (for now you can use XStyle and DarkReader, for example)
- [ ] Better support for mobile screens (help wanted!)
- [ ] Add proper styling for `<sound>` tags

## Usage

### Dependencies

This project utilises some Python 3.10 features, such as the `match` syntax, and a minimal set of dependencies:
```
flask
flask-cors
waitress
```

### Local Deployment

The simplest method to use this app is to run it locally. I would recommend running the custom HTTP server in the `http_server` sub-directory, which forwards requests under `/api` to the backend, and serves static files in `.dist/`.

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

Assuming your distribution uses `systemd`, you can refer to the provided sample `systemd` [config](/silverdict.service) and run the script as a service.

NB: currently the API server is memory-inefficient due to the way `MDictReader` is designed. Running the server with eight mid- to large-sized dictionaries consumes ~250 MB of memory.

## Similar projects

I had no idea of these similar projects in the course of development. So please take a look at them and choose your favourite:

- [flask-mdict](https://github.com/liuyug/flask-mdict): it is very similar to mine, but adopts a more GoldenDict-like interface (where definitions of the same entry from different dictionaries are compiled into a single page.) This web-app also displays word frequency data.
- [mdx-server](https://github.com/ninja33/mdx-server): only one dictionary is accessible at once.
- [mdict-query](https://github.com/mmjang/mdict-query): another MDict library that uses SQLite to index dictionaries.

Note that these projects only have the MDict format in mind, while I plan to support three additional common formats.