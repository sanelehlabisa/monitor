FROM node:24.15.0-alpine3.23 AS base

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

FROM base AS development
EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

FROM base AS build
RUN npm run build

FROM nginx:1.30.8-alpine@sha256:8eb04fe3b385090e9aa02961f77398ad09b6bf33ab07f6669a5bb7acce22c0d3 AS production
ENV NGINX_ENVSUBST_FILTER=^APP_URL$
COPY nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
