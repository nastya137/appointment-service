# Appointment Booking System

Fullstack система записи на консультацию.

## Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL/SQLite
- Telegram Bot

### Frontend
- Vue 3
- TypeScript
- Vite
- Tailwind CSS

## Features

- выбор специалиста
- выбор услуги специалиста
- выбор даты
- получение свободных временных слотов
- создание записи
- Telegram bot integration

## Docker: локальная разработка

Нужен запущенный Docker Desktop в режиме Linux containers с Docker Compose.
Все команды ниже выполняются из папки с `compose.yaml` (внутренняя
`python-bot-main`, рядом с `app` и `frontend`). Python и Node.js на компьютере
для этого способа запуска не нужны.

### Первый запуск

1. Создайте `.env` из примера, если файла ещё нет. В PowerShell:

   ```powershell
   if (-not (Test-Path .env)) { Copy-Item .env.example .env }
   ```

2. Укажите `BOT_TOKEN` в `.env`. Токен передаётся только контейнеру бота,
   в образы и переменные фронтенда он не включается. Запускайте один экземпляр
   polling-бота с этим токеном: остановите ранее запущенный вручную экземпляр.

3. Соберите и запустите сервисы:

   ```sh
   docker compose up --build -d
   docker compose ps -a
   docker compose logs --tail=50 bot
   ```

   Проверить фронтенд и API без токена можно отдельно:

   ```sh
   docker compose up --build -d --wait backend frontend
   ```

   Без `BOT_TOKEN` контейнер бота завершится с сообщением `BOT_TOKEN is not set`.
   После заполнения `.env` выполните `docker compose up -d bot`:
   обычный `restart` не применяет новые переменные окружения.

4. Для демонстрационной формы заполните новую базу тестовыми данными:

   ```sh
   docker compose exec backend python -m app.seed
   ```

   Seed запускается вручную; при обычном старте таблицы создаются автоматически,
   но демонстрационные записи не добавляются. Форма пока использует тестового
   пользователя `id = 1`, который появляется при заполнении новой базы.

Адреса:

- Фронтенд: <http://127.0.0.1:5173>.
- Документация API: <http://127.0.0.1:8000/docs>.
- Проверка API и подключения к БД: <http://127.0.0.1:8000/health>.

Используйте именно `127.0.0.1`: этот origin разрешён текущими настройками CORS.
Оба опубликованных порта доступны только с локального компьютера. Бот получает
обновления через исходящие запросы к Telegram и не требует опубликованного порта.

### Как устроен запуск

- `backend` собирает образ `appointment-booking-python:dev` и запускает FastAPI
  через Uvicorn с перезагрузкой при изменении Python-кода.
- `bot` использует этот же образ и обращается к `http://backend:8000`.
  Сборка Python-образа описана у `backend`; команда `up --build` собирает его
  перед запуском зависимого бота.
- `frontend` запускает Vite в Node.js-контейнере. Запросы из браузера идут на
  `http://127.0.0.1:8000`, поэтому внутреннее имя `backend` фронтенду не передаётся.
- Бот и фронтенд стартуют после успешного healthcheck API. `/health` проверяет
  подключение к БД и возвращает HTTP 503 при ошибке базы.
- Исходники подключены с компьютера. Для Vite и Uvicorn включён polling файлов,
  чтобы изменения из Windows обнаруживались в Linux-контейнерах Docker Desktop.
- Python-контейнеры видят только папку `app`; локальная корневая `.env` туда
  не монтируется. Linux-зависимости фронтенда хранятся в отдельном volume
  `frontend_node_modules`, независимо от Windows-папки `frontend/node_modules`.

### Данные и настройки

SQLite находится в `/data/database.db` бэкенда, в именованном volume `sqlite_data`.
Обычные перезапуски, пересборка образа и `docker compose down` сохраняют базу.
`docker compose down -v` удаляет volumes, включая базу данных.

Compose начинает с отдельной пустой базы и не переносит существующий локальный
`database.db`. Если нужен перенос данных, сначала сделайте резервную копию
исходной базы; seed не заменяет перенос.

В Compose адрес БД фиксирован на путь внутри volume. `DATABASE_URL` и
`API_BASE_URL` из `.env.example` предназначены для запуска Python без Docker.
Пустой `DATABASE_URL` при таком запуске использует прежний путь `./database.db`.
Настройки адреса API фронтенда в Compose также имеют приоритет над `.env` Vite.

### Повседневные команды

```sh
# Логи всех сервисов / только бота
docker compose logs -f
docker compose logs -f bot

# Перезапуск бота после изменения его кода
docker compose restart bot

# Применить изменения Python-зависимостей и пересоздать оба Python-контейнера
docker compose up --build -d --force-recreate backend bot

# Остановить систему, сохранив данные
docker compose down
```

После изменения `frontend/package.json` или lock-файла обновите зависимости
в Linux-volume и пересоберите образ:

```sh
docker compose stop frontend
docker compose run --rm --no-deps frontend npm ci --no-audit --no-fund
docker compose up --build -d frontend
```

Проверки фронтенда внутри контейнера:

```sh
docker compose exec frontend npm run lint
docker compose exec frontend npm run build
```

Это конфигурация разработки с Vite и Uvicorn `--reload`. Для публичного сервера
нужны отдельная конфигурация запуска, собранный фронтенд и HTTPS.

### Проверки настроек API

При установленном Python с зависимостями проекта:

```sh
python -m unittest discover -s tests -v
```

Тесты используют временные базы: проверяют `DATABASE_URL`, создание таблиц,
успешный healthcheck и HTTP 503 при недоступности БД. В Telegram не обращаются.
