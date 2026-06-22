# Безопасность SKMY

## Уже реализовано

- **Login:** admin-панель использует Flask-Login; анонимные пользователи перенаправляются на страницу входа.
- **Password hashing:** пароли не хранятся открытым текстом; используется хэширование Werkzeug.
- **CSRF:** Flask-WTF CSRFProtect защищает POST-формы login, logout, CRUD, публикацию/скрытие и обработку обращений.
- **Admin protection:** доступ к `/admin` и admin-blueprint’ам требует аутентифицированного пользователя с ролью `admin`.
- **Audit Log:** изменения путеводителя, новостей и обработка обращений записываются в `AdminLog`.

## Что необходимо завершить перед production

### Rate limiting

Добавить ограничение частоты запросов как минимум для `/admin/login`, контактной формы и поиска. Это снизит риск brute-force и автоматического спама.

### Security headers

Добавить заголовки через Nginx или Flask-конфигурацию: Content-Security-Policy, X-Content-Type-Options, Referrer-Policy, X-Frame-Options или frame-ancestors в CSP, Permissions-Policy и Strict-Transport-Security после полного перехода на HTTPS.

### Session hardening

В production включить безопасные cookie-настройки: `SESSION_COOKIE_SECURE=True`, `SESSION_COOKIE_HTTPONLY=True`, разумный `PERMANENT_SESSION_LIFETIME` и `SESSION_COOKIE_SAMESITE='Lax'` либо более строгий вариант после проверки всех форм.

### Production SECRET_KEY

Сгенерировать длинный случайный `SECRET_KEY` и хранить только в защищённом `.env`. Нельзя использовать development fallback из `config.py` в production. При утечке ключ нужно немедленно заменить: это завершит текущие пользовательские сессии.

### HTTPS-only cookies

После подключения SSL все сессионные и CSRF-связанные cookie должны передаваться только по HTTPS. Также включить автоматический HTTP → HTTPS redirect в Nginx/Certbot.

## Операционные правила

- Не хранить `.env`, дампы БД и пароли в Git.
- Ограничить права системного пользователя приложения и PostgreSQL-роли.
- Регулярно обновлять зависимости и ОС после проверки changelog.
- Просматривать Audit Log и логи Nginx/Gunicorn на подозрительные действия.
- Перед обновлением production создавать backup и иметь проверенную процедуру восстановления.
