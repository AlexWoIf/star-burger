# Build js scripts
FROM node:16.16.0-alpine as nodejs-frontend
WORKDIR /frontend
COPY . .
RUN npm ci
RUN ./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
