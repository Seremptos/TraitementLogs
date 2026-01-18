FROM node:22-alpine

# install simple http server for serving static content
RUN npm install -g http-server

COPY ./package*.json ./

RUN npm install

COPY . .

# build app for production with minification
RUN npm run build

EXPOSE 4000

CMD ["http-server", "dist", "-a", "0.0.0.0", "-p", "4000"]
