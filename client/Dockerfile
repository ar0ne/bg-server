# syntax=docker/dockerfile:1.4

FROM node:lts AS build

WORKDIR /app
COPY package.json /app/package.json
COPY package-lock.json /app/package-lock.json

RUN npm ci
COPY . /app

RUN ["npm", "run", "build:staging"]

# Nginx
FROM nginx:1.13-alpine

COPY --from=build /app/build /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]