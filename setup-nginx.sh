#!/bin/bash

# Настройка nginx и SSL для libertylib.online
# Запускать с правами sudo

set -e

DOMAIN=libertylib.online
EMAIL=admin@$DOMAIN
API_PORT=8000

# Установка nginx и certbot
if ! command -v nginx &> /dev/null; then
    apt update && apt install -y nginx
fi
if ! command -v certbot &> /dev/null; then
    apt install -y certbot python3-certbot-nginx
fi

# Остановка nginx для получения сертификатов
systemctl stop nginx || true

# Получение сертификата для домена
certbot certonly --standalone --non-interactive --agree-tos --email $EMAIL -d $DOMAIN || true

# Копирование nginx конфига
if [ ! -f nginx.conf.template ]; then
    echo "❌ nginx.conf.template не найден!"; exit 1;
fi
cp nginx.conf.template /etc/nginx/sites-available/libertylib
ln -sf /etc/nginx/sites-available/libertylib /etc/nginx/sites-enabled/libertylib

# Отключаем дефолтный сайт
if [ -L /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
fi

# Проверка и запуск nginx
nginx -t && systemctl restart nginx

# Настройка автопродления сертификатов
if ! crontab -l | grep -q 'certbot renew'; then
    (crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --post-hook 'systemctl reload nginx'") | crontab -
fi

echo "🎉 Nginx и SSL для $DOMAIN настроены!"
echo "- Frontend: https://$DOMAIN"
echo "- Backend API: https://$DOMAIN/api/" 