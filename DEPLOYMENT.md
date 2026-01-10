# Развертывание на продакшене

## Подготовка

### 1. Переменные окружения

Создать `.env` файл с production переменными:

```
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### 2. Безопасность

- Изменить SECRET_KEY
- Установить DEBUG=False
- Использовать HTTPS
- Настроить CORS если необходимо
- Использовать PostgreSQL вместо SQLite
- Настроить резервное копирование БД

### 3. Статические файлы

```bash
python manage.py collectstatic
```

### 4. Развертывание на Heroku

```bash
heroku login
heroku create your-app-name
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

### 5. Развертывание на DigitalOcean

Следовать документации DigitalOcean для Django приложений.
