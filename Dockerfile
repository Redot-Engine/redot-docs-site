FROM node:24-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN chown -R node:node /app

USER node

EXPOSE 3000

CMD ["npm", "start", "--", "--host", "0.0.0.0"]
