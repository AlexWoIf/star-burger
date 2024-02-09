#! /bin/bash

set -ex

git pull
pip install -r requirements.txt
npm ci
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
python manage.py collectstatic --noinput
python manage.py migrate --noinput
systemctl restart star_burger_django
