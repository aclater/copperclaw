FROM node:20-alpine AS build
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build

FROM registry.access.redhat.com/ubi9/nginx-120:latest
COPY --from=build /app/dist /opt/app-root/src
COPY nginx.default.d/ /opt/app-root/etc/nginx.default.d/
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
