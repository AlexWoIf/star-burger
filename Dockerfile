# Build js scripts
FROM node:16.16.0-alpine as nodejs-frontend
WORKDIR /frontend
COPY frontend/ .
RUN npm ci
RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

# Build Django staticfiles
FROM python:3.9-slim-bookworm as django-app

WORKDIR /usr/src/app

RUN --mount=type=bind,source=backend/requirements.txt,target=/tmp/requirements.txt \
    pip install --no-cache-dir --requirement /tmp/requirements.txt
COPY backend/ .
COPY --from=nodejs-frontend /frontend/bundles ./bundles/
RUN export SECRET_KEY=build_stage_key && \
    export DATABASE_URL=sqlite:///db.sqlite3 && \
    python manage.py collectstatic --noinput

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8000", "star_burger.wsgi:application"]