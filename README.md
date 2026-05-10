# fast-api-blogicum

# Запуск в Docker

```bash
docker compose up --build
```

`docker-compose.yml` поднимает 2 контейнера:
- `db` — PostgreSQL
- `app` — FastAPI

При старте контейнера `app` автоматически выполняет миграции и запускает API:

```bash
alembic upgrade head
uvicorn main:app --host ${APP_HOST} --port ${APP_PORT}
```

При создании поста `POST /posts/` можно отправить файл изображения в поле `image_file`
(`multipart/form-data`, поддерживаются `image/png` и `image/jpeg`). Путь к сохраненному файлу
записывается в поле `image` поста.

Настройки приложения загружаются из файла `.env` через `Pydantic Settings`.

## Подключение к PostgreSQL

Параметры находятся в `.env`:

```env
POSTGRES_DB=blogicum
POSTGRES_USER=blogicum_user
POSTGRES_PASSWORD=blogicum_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg://blogicum_user:blogicum_password@db:5432/blogicum
```

Остановка и удаление контейнеров:

```bash
docker compose down
```

Остановка с удалением тома PostgreSQL (полный сброс БД):

```bash
docker compose down -v
```

# Полезные команды для работы с alembic

```bash
# Показать текущую версию
alembic current

# Показать историю миграций
alembic history

# Откатиться на шаг назад
alembic downgrade -1

# Откатиться до конкретной ревизии
alembic downgrade <revision_id>

# Обновить до последней версии
alembic upgrade head

# Создать пустую миграцию вручную
alembic revision -m "add column to users"

# Показать SQL, который будет выполнен
alembic upgrade head --sql
```