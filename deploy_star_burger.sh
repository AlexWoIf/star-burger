#! /bin/bash

set -e

git pull
pip install -r requirements.txt
npm ci
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
python manage.py collectstatic --noinput
python manage.py migrate --noinput
systemctl restart star_burger_django

. .env
curl --request POST \
     --url https://api.rollbar.com/api/1/deploy \
     --header 'X-Rollbar-Access-Token: $ROLLBAR_TOKEN' \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
{
  "environment": "$ROLLBAR_TOKEN",
  "revision": "$(git rev-parse HEAD)",
  "comment": "deploy script",
  "local_username": "$USER"
}
'

echo "Deploy successful!!!"