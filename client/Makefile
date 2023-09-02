dist: src/App.vue
	yarn build && rm -r ../http_server/dist && cp -r dist ../http_server && rm -r /srv/www/htdocs/* && mv dist/* /srv/www/htdocs && rm -r dist