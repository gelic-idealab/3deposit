# FROM node:lts-alpine
# # make the 'app' folder the current working directory
# WORKDIR /app
# # copy both 'package.json' and 'package-lock.json' (if available)
# COPY package*.json ./
# # install project dependencies
# RUN npm install
# # copy project files and folders to the current working directory (i.e. 'app' folder)
# COPY . .
# # # build app for production with minification
# # RUN npm run build
# EXPOSE 8080

FROM node:10
COPY ./ /app
WORKDIR /app
RUN npm install && npm run build

FROM nginx
RUN mkdir /app
COPY --from=0 /app/dist /app
COPY nginx.conf /etc/nginx/nginx.conf