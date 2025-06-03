FROM node:18-alpine

WORKDIR /app

COPY frontend/package*.json ./

RUN npm install

COPY frontend/ .

# Собираем production build
RUN npm run build

EXPOSE 3000

# Добавляем скрипт для копирования статики в volume и запуска dev сервера
CMD sh -c "cp -r /app/dist/* /app/dist/. 2>/dev/null || true && npm run dev" 