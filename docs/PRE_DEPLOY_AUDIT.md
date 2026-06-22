# Pre-deploy audit: SKMY Website

Дата аудита: 2026-06-22  
Тип аудита: read-only. Код, база данных, маршруты и конфигурация не изменялись.

## Итог

Приложение функционально готово к дальнейшей production-подготовке, но **не должно переноситься на публичный VPS без устранения критических рисков ниже**. Главные блокеры: предсказуемый fallback для `SECRET_KEY`, хардкод первого admin-пароля, отсутствие production-конфигурации и session hardening, локальные URL в SEO и отсутствие правил `.gitignore`.

## Проверенная структура проекта

Проект имеет ожидаемые каталоги Flask-приложения:

- `routes/` — public и admin blueprints;
- `templates/` и `static/` — интерфейс и стили;
- `database/` — SQLAlchemy и модели;
- `docs/` — документация;
- `requirements.txt` и `.env.example`;
- `backups/`, `logs/`, `nginx/`, `services/` — заготовки для инфраструктуры.

В корне присутствует `.env`. Его содержимое намеренно не проверялось и не выводилось в рамках безопасного аудита.

### Риск: Git-репозиторий недоступен из текущей рабочей копии

Команды `git status` и `git ls-files` завершились ошибкой `not a git repository`. Поэтому невозможно подтвердить, что `.env`, backup-файлы и локальные данные не отслеживаются Git.

**Рекомендация до переноса:** проверить, что production-репозиторий и рабочая копия корректно инициализированы; добавить правила игнорирования для `.env`, `venv/`, `__pycache__/`, `backups/`, `logs/`, дампов PostgreSQL и upload-файлов.

## requirements.txt

### Что проверено

Основные runtime-зависимости закреплены версиями: Flask, Flask-Login, Flask-SQLAlchemy, Flask-WTF, SQLAlchemy, psycopg2-binary, python-dotenv и Werkzeug. Для текущего приложения этого достаточно.

### Риски и рекомендации

1. **Gunicorn/Waitress отсутствуют в requirements.txt.** В `DEPLOYMENT.md` Gunicorn устанавливается отдельной командой, но production runtime должен быть воспроизводим из зависимостей проекта.
   - До переноса: добавить выбранный WSGI-сервер в production requirements или создать отдельный `requirements-prod.txt`.
2. **Нужна проверка актуальности зависимостей перед релизом.**
   - До переноса: выполнить dependency/security scan и обновить пакеты только после тестирования.
3. **`psycopg2-binary` работает для MVP, но требует осознанного production-решения.**
   - До переноса: подтвердить, что этот пакет допустим для выбранного образа/ОС, либо перейти на подходящую production-сборку драйвера по отдельной задаче.

## `.env.example`

### Что проверено

Шаблон не содержит реальных секретов. В нём присутствуют `SECRET_KEY`, `DATABASE_URL`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `BASE_URL`, почтовые переменные и текущие `DB_*` параметры.

### Риски и рекомендации

1. **`DATABASE_URL`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` и `BASE_URL` сейчас не используются приложением.** Текущий `config.py` читает только `SECRET_KEY` и `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`.
   - До переноса: выбрать единый формат конфигурации и либо реализовать использование этих переменных отдельной задачей, либо явно пометить их как будущие/необязательные в шаблоне.
2. **Не подтверждено, что `.env` игнорируется Git.**
   - До переноса: заполнить `.gitignore` и проверить `git status --ignored` в корректном репозитории.
3. **Production `.env` должен иметь права `600`.**
   - До переноса: создать `.env` на VPS от отдельного пользователя приложения, не копировать development-секреты.

## PostgreSQL connection settings

### Что проверено

`config.py` создаёт PostgreSQL URL через SQLAlchemy `URL.create` с драйвером `postgresql+psycopg2`. Параметры читаются из `DB_*`; SQLAlchemy tracking отключён.

### Риски и рекомендации

1. **Нет проверки обязательных DB-переменных.** При пустом `DB_USER`, `DB_PASSWORD` или `DB_NAME` приложение может завершиться неочевидной ошибкой подключения.
   - До переноса: добавить явную production-валидацию окружения отдельной задачей или проверить все значения при deploy.
2. **Нет явных SSL-параметров PostgreSQL.**
   - До переноса: если БД находится не на localhost, настроить TLS (`sslmode=require` или более строгий режим) и сетевые правила PostgreSQL.
3. **Нет pool health settings.**
   - Рекомендация: для long-running Gunicorn workers рассмотреть `pool_pre_ping`, `pool_recycle` и ограничение размера пула после оценки нагрузки.
4. **Нет миграций схемы.** Сейчас `init-db` использует `db.create_all()`.
   - До первого релиза: это допустимо для начального создания таблиц; до дальнейшего развития требуется отдельный план миграций, например Alembic/Flask-Migrate. Не применять `create_all()` как замену миграциям на уже изменяемой production-схеме.

## Production config и debug

### Что проверено

В проекте есть единый `Config`. `app.run(debug=True)` расположен только в блоке `if __name__ == "__main__"`; Gunicorn, импортирующий `app:app`, его не выполнит.

### Риски и рекомендации

1. **Нет отдельной production-конфигурации и нет явного `DEBUG=False`.**
   - До переноса: создать отдельную production-конфигурацию или явные production environment settings; запускать только WSGI-сервером, не `python app.py`.
2. **Нет настройки trusted proxy.** За Nginx приложение не учитывает `X-Forwarded-*` через `ProxyFix`.
   - До переноса: определить и безопасно настроить доверие к одному reverse proxy; это важно для HTTPS-определения, URL и cookie.
3. **Нет production logging policy.**
   - До переноса: настроить структурированный журнал Gunicorn/Nginx, ротацию логов и мониторинг ошибок.

## SECRET_KEY

### Что проверено

`Config.SECRET_KEY` берёт значение из окружения, но имеет fallback `"dev-secret-key"`.

### Критический риск

Если production `.env` отсутствует или переменная пуста, приложение будет использовать предсказуемый development key. Это ставит под риск подпись Flask session и CSRF-токены.

**Исправление до переноса:** запретить fallback в production, сгенерировать криптографически случайный ключ и обеспечить fail-fast запуск при отсутствии `SECRET_KEY`.

## Session settings

### Что проверено

Flask-Login и CSRF подключены. Явные session cookie settings в `config.py` отсутствуют.

### Риски и рекомендации

1. **Не заданы `SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`, `SESSION_COOKIE_SAMESITE`.**
   - До переноса: после HTTPS включить `Secure=True`, `HttpOnly=True`, `SameSite=Lax` (или более строгий проверенный вариант).
2. **Не задан срок жизни permanent session.**
   - До переноса: определить `PERMANENT_SESSION_LIFETIME` и политику истечения admin-сессий.
3. **Нет rate limiting на login.**
   - До переноса: добавить ограничение попыток для `/admin/login`; также ограничить контактную форму и поиск по необходимости.

## Sitemap и robots

### Что проверено

- `/robots.txt` отвечает HTTP 200 и содержит `Allow: /`.
- `/sitemap.xml` отвечает HTTP 200 и включает публичные статические URL, опубликованные новости, активные категории и опубликованные статьи.
- sitemap не включает admin-URL.

### Блокирующий production-риск

`routes/public/seo.py` содержит хардкод `http://127.0.0.1:5000` в `robots.txt` и `sitemap.xml`. `templates/base.html` использует тот же локальный base URL для canonical и hreflang.

**Исправление до переноса:** получать base URL из конфигурации, в production использовать `https://skmy.fi`, обновить robots, sitemap, canonical и hreflang. После deploy проверить через браузер и Google Search Console.

### Дополнительная рекомендация

Robots сейчас разрешает весь путь `/`, включая `/admin`. Login защищает admin от доступа к данным, но служебные URL могут быть обнаружены поисковыми системами.

- До переноса: решить SEO-политику для `/admin` (обычно `Disallow: /admin`) и при необходимости добавить `noindex` для admin-шаблонов.

## Admin login flow

### Что проверено

Read-only test client проверка прошла:

- анонимный запрос к `/admin` получает `302` на `/admin/login`;
- POST на `/admin/login` без CSRF-токена получает `400`;
- login с корректным CSRF-токеном и существующим admin-пользователем получает `302` на `/admin/`;
- после login `/admin` отвечает `200`.

### Риски и рекомендации

1. **Критический риск: `create-admin` содержит хардкод credentials.** В `app.py` email `admin@skmy.local` и пароль `AdminDev2026Pass` встроены в исходный код; переменные `ADMIN_EMAIL` и `ADMIN_PASSWORD` из `.env.example` не используются.
   - До переноса: заменить команду на безопасное получение email/password из environment или интерактивный ввод; не использовать этот известный пароль в production.
2. **Нет rate limiting и временной блокировки после неудачных логинов.**
   - До переноса: добавить rate limiting и мониторинг неуспешных попыток.
3. **Redirect после login всегда ведёт на `/admin/`.** Параметр `next` создаётся Flask-Login, но не используется.
   - Рекомендация: это не блокер; при улучшении обработать `next` с проверкой на open redirect.
4. **Не проверена политика password rotation/recovery.**
   - До переноса: определить процедуру безопасной смены admin-пароля и аварийного восстановления доступа.

## Список исправлений до переноса на VPS

### Блокеры

- [ ] Убрать production fallback `dev-secret-key`; требовать уникальный `SECRET_KEY`.
- [ ] Убрать хардкод `AdminDev2026Pass` и создать безопасный production flow для первого администратора.
- [ ] Вынести `http://127.0.0.1:5000` из robots, sitemap, canonical и hreflang в production `BASE_URL=https://skmy.fi`.
- [ ] Заполнить `.gitignore` и подтвердить, что `.env`, venv, backup и логи не попадают в Git.
- [ ] Добавить/зафиксировать Gunicorn или другой WSGI-сервер в production-зависимостях.
- [ ] Настроить production config: `DEBUG=False`, HTTPS и безопасные session cookie flags.

### До запуска домена

- [ ] Проверить реальные значения `DB_*` и доступ PostgreSQL с VPS.
- [ ] Настроить Nginx, SSL, systemd и firewall по `DEPLOYMENT.md`.
- [ ] Настроить регулярный PostgreSQL backup и проверить восстановление по `BACKUP.md`.
- [ ] Добавить rate limiting для login и публичных форм.
- [ ] Добавить security headers и безопасную настройку reverse proxy.
- [ ] Проверить мобильную версию, accessibility и все публичные страницы на `https://skmy.fi`.
- [ ] Проверить sitemap, robots, canonical/hreflang в production и зарегистрировать сайт в Google Search Console.

## Вывод

Функциональная часть MVP работает: login и CSRF проверены, SEO-маршруты отвечают, public/admin blueprints разделены. Production-перенос следует выполнять после устранения блокеров, прежде всего секретов, admin bootstrap credentials, URL-конфигурации, session hardening и Git hygiene.
