# Развёртывание SKMY на VPS

Этот документ описывает рекомендуемый production-путь для домена `skmy.fi`: Linux VPS, PostgreSQL, Gunicorn, Nginx и HTTPS. Перед первым развёртыванием убедитесь, что локальные изменения закоммичены в Git и проверены.

## 1. Подготовить VPS

Подходит актуальный Ubuntu/Debian VPS. Установите базовые пакеты:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip postgresql nginx certbot python3-certbot-nginx
```

Создайте отдельного системного пользователя для приложения и каталог проекта. Не запускайте Flask/Gunicorn от `root`.

```bash
sudo adduser --system --group --home /srv/skmy skmy
sudo mkdir -p /srv/skmy
sudo chown skmy:skmy /srv/skmy
```

## 2. PostgreSQL

Создайте отдельную роль и базу данных. Пароль нужно хранить только в `.env`, а не в Git.

```bash
sudo -u postgres createuser --pwprompt skmy_user
sudo -u postgres createdb --owner=skmy_user skmy_website_db
```

Проверьте, что роль имеет доступ только к необходимой базе. После переноса проекта выполните создание таблиц:

```bash
cd /srv/skmy/skmy_website
source venv/bin/activate
flask --app app init-db
flask --app app create-admin
```

## 3. Получить проект и создать Python venv

```bash
sudo -u skmy git clone <REPOSITORY_URL> /srv/skmy/skmy_website
cd /srv/skmy/skmy_website
sudo -u skmy python3 -m venv venv
sudo -u skmy venv/bin/pip install --upgrade pip
sudo -u skmy venv/bin/pip install -r requirements.txt
```

## 4. Настроить `.env`

Скопируйте шаблон и заполните секреты только на сервере:

```bash
cd /srv/skmy/skmy_website
sudo -u skmy cp .env.example .env
sudo -u skmy chmod 600 .env
```

Нужны уникальный production `SECRET_KEY`, параметры БД и production `BASE_URL=https://skmy.fi`. Текущий `config.py` использует `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` и `DB_NAME`; `DATABASE_URL` в шаблоне оставлен для будущей унификации конфигурации.

Никогда не коммитьте `.env` в Git. Добавьте его в `.gitignore` до production-релиза.

## 5. Запуск через Gunicorn

Для Linux VPS рекомендуется Gunicorn. Установите его в venv:

```bash
sudo -u skmy /srv/skmy/skmy_website/venv/bin/pip install gunicorn
```

Проверьте запуск вручную:

```bash
cd /srv/skmy/skmy_website
sudo -u skmy venv/bin/gunicorn --bind 127.0.0.1:8000 app:app
```

Для Windows-среды вместо Gunicorn можно использовать Waitress, но на Linux VPS для production предпочтителен Gunicorn.

### systemd: запуск после перезагрузки

Создайте `/etc/systemd/system/skmy.service`:

```ini
[Unit]
Description=SKMY Flask application
After=network.target postgresql.service

[Service]
User=skmy
Group=skmy
WorkingDirectory=/srv/skmy/skmy_website
EnvironmentFile=/srv/skmy/skmy_website/.env
ExecStart=/srv/skmy/skmy_website/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Активируйте сервис:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now skmy
sudo systemctl status skmy
```

Логи приложения:

```bash
sudo journalctl -u skmy -f
```

## 6. Nginx reverse proxy

Создайте `/etc/nginx/sites-available/skmy.fi`:

```nginx
server {
    listen 80;
    server_name skmy.fi www.skmy.fi;

    location /static/ {
        alias /srv/skmy/skmy_website/static/;
        expires 7d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Включите конфигурацию и проверьте Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/skmy.fi /etc/nginx/sites-enabled/skmy.fi
sudo nginx -t
sudo systemctl reload nginx
```

## 7. SSL-сертификат

После того как DNS-записи `skmy.fi` и `www.skmy.fi` указывают на VPS, выпустите сертификат Let's Encrypt:

```bash
sudo certbot --nginx -d skmy.fi -d www.skmy.fi
```

Проверьте автоматическое продление:

```bash
sudo systemctl status certbot.timer
sudo certbot renew --dry-run
```

После включения HTTPS настройте production cookie-параметры и `BASE_URL=https://skmy.fi`.

## 8. Обновление проекта через Git

Перед обновлением сделайте backup PostgreSQL по инструкции в `BACKUP.md`.

```bash
cd /srv/skmy/skmy_website
sudo -u skmy git fetch origin
sudo -u skmy git pull --ff-only origin main
sudo -u skmy venv/bin/pip install -r requirements.txt
sudo -u skmy venv/bin/python -m compileall app.py routes database
sudo systemctl restart skmy
sudo systemctl status skmy
```

После обновления проверьте главную страницу, `/robots.txt`, `/sitemap.xml`, login и admin-панель. При будущих миграциях БД выполнять их нужно только по отдельной документированной процедуре.
