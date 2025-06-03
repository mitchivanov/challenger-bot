# Этап сборки
FROM node:20-alpine as builder

WORKDIR /app

# Копирование файлов package.json и package-lock.json
COPY package*.json ./

# Установка зависимостей
RUN npm ci

# Копирование исходного кода
COPY . .

# Сборка приложения
RUN npm run build

# Этап production - копируем в volume для nginx
FROM alpine:latest

# Копирование собранного приложения в nginx volume
COPY --from=builder /app/dist /usr/share/nginx/html

# Контейнер завершается после копирования файлов
CMD ["echo", "Frontend static files copied to volume"] 