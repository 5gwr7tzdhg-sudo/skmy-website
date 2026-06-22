# Final local pre-deploy audit: SKMY

Дата аудита: 2026-06-22  
Режим: локальный, read-only. Код, база данных и конфигурационные файлы не изменялись.

## Итоговый статус

Локальная функциональная проверка прошла успешно. Публичные страницы, SEO-маршруты, admin login/logout, CSRF и защита admin-разделов работают.

Проект **можно готовить к VPS**, но перед фактическим production-запуском необходимо задать реальные production environment variables, установить зависимости на VPS и проверить Git-репозиторий в нормальной clone-копии.

## Что проверено и прошло

### Публичные маршруты

Все перечисленные маршруты вернули HTTP 200:

- [x] `/fi/`
- [x] `/ru/`
- [x] `/en/`
- [x] `/ru/about`
- [x] `/ru/news`
- [x] `/ru/guide`
- [x] `/ru/interpreting`
- [x] `/ru/contacts`
- [x] `/ru/search?q=kela`

### SEO

- [x] `/robots.txt` возвращает HTTP 200 и содержит ссылку на sitemap.
- [x] `/sitemap.xml` возвращает HTTP 200.
- [x] Sitemap формируется с URL из `Config.BASE_URL`.
- [x] Canonical на `/ru/` формируется из `Config.BASE_URL`.
- [x] Hreflang для `fi`, `ru` и `en` присутствует на публичной странице.

Текущая локальная конфигурация использует `BASE_URL=http://127.0.0.1:5000`. Это корректно для локальной проверки. Для VPS обязательно задать `BASE_URL=https://skmy.fi`; при `ENV=production` отсутствие `BASE_URL` блокирует запуск.

### Admin и CSRF

- [x] Анонимный запрос к `/admin` получает `302` на `/admin/login`.
- [x] `/admin/login` доступен без авторизации и возвращает HTTP 200.
- [x] Login с корректным CSRF-токеном работает и возвращает `302` на `/admin/`.
- [x] Login без CSRF-токена возвращает HTTP 400.
- [x] Logout с CSRF-токеном работает и возвращает `302` на `/admin/login`.
- [x] После входа доступны:
  - `/admin/guide/categories`;
  - `/admin/news`;
  - `/admin/contacts`;
  - `/admin/logs`.

### Security и конфигурация

- [x] Отсутствующий `SECRET_KEY` приводит к явной ошибке старта.
- [x] `create-admin` без `ADMIN_EMAIL` и `ADMIN_PASSWORD` завершается ошибкой и не создаёт пользователя.
- [x] При `ENV=production` задано `SESSION_COOKIE_SECURE=True`.
- [x] `SESSION_COOKIE_HTTPONLY=True`.
- [x] `SESSION_COOKIE_SAMESITE=Lax`.
- [x] `.gitignore` содержит `.env`, `venv/`, `logs/`, `backups/` и остальные необходимые правила.

### Файлы и документация

- [x] `.env.example` существует.
- [x] `requirements.txt` содержит Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, psycopg2-binary, python-dotenv, Werkzeug, gunicorn и waitress.
- [x] `docs/DEPLOYMENT.md` существует.
- [x] `docs/BACKUP.md` существует.
- [x] `docs/SECURITY.md` существует.
- [x] `docs/PRODUCTION_CHECKLIST.md` существует.
- [x] `docs/PRE_DEPLOY_AUDIT.md` существует.
- [x] `docs/MVP_STATUS.md` существует.

## Что осталось перед реальным VPS deploy

### Обязательные действия

- [ ] На VPS создать реальный `.env` с уникальным `SECRET_KEY`.
- [ ] Установить `ENV=production`.
- [ ] Установить `BASE_URL=https://skmy.fi`.
- [ ] Задать реальные `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`.
- [ ] Задать безопасные `ADMIN_EMAIL` и `ADMIN_PASSWORD` перед первым запуском `create-admin`.
- [ ] Установить production-зависимости командой `pip install -r requirements.txt`.
- [ ] Настроить Gunicorn или Waitress, Nginx, systemd и SSL по `DEPLOYMENT.md`.
- [ ] Настроить и проверить PostgreSQL backup по `BACKUP.md`.

### Локальные ограничения аудита

1. **Gunicorn и Waitress не установлены в текущем локальном venv.** Они уже закреплены в `requirements.txt`; это не блокирует разработку, но на VPS нужно выполнить установку зависимостей.
2. **Git status недоступен в текущем workspace.** Путь `.git` существует, но Git сообщает `not a git repository`. Поэтому нельзя окончательно подтвердить, что `.env` не был закоммичен в истории или не отслеживается в текущей копии.
   - Перед push: открыть проект из корректной Git clone-копии и выполнить:

```bash
git status --short
git check-ignore -v .env
git ls-files .env
```

Ожидаемый результат: `.env` игнорируется, а `git ls-files .env` не выводит файл.

## Можно ли пушить в Git?

**Условно да, после проверки Git в корректной repository-копии.**

`.gitignore` содержит нужные правила, а `.env.example` не содержит секретов. Однако в текущем workspace Git-метаданные неработоспособны, поэтому аудит не может подтвердить историю и индекс. Нельзя пушить `.env`, дампы БД, backups, логи или venv.

## Можно ли готовить VPS?

**Да.** Документация, requirements и основные production guards готовы. Можно подготовить VPS, PostgreSQL, Nginx, systemd и DNS.

**Не следует включать публичный production-трафик**, пока не будут выполнены пункты из раздела «Что осталось перед реальным VPS deploy», прежде всего реальные секреты, `ENV=production`, `BASE_URL=https://skmy.fi`, SSL, backup и проверка Git hygiene.

## Вывод

Локальный MVP прошёл требуемый функциональный и security smoke-test. Основные code-level pre-deploy риски устранены. Оставшиеся задачи относятся к production environment и инфраструктуре, а не к публичным маршрутам, admin-функциональности или базе данных.
