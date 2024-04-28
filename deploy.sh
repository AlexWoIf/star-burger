#!/bin/bash

git pull https://github.com/AlexWoIf/star-burger.git
cd star-burger
docker compose up -d
mkdir -p media
mkdir -p static
mount --bind /var/lib/docker/volumes/star-burger_static/_data/ /opt/star-burger/static/
mount --bind /var/lib/docker/volumes/star-burger_media/_data/ /opt/star-burger/media/
cp starburger_docker /etc/nginx/sites-available
ln -s /etc/nginx/sites-available/starburger_docker /etc/nginx/sites-enabled
nginx -s reload