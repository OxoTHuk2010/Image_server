# Image Hosting (Flask + Postgres + Nginx)

## Быстрый старт (Docker)
1. Убедитесь, что установлен Docker + docker-compose (или Docker Compose v2).
2. В корне проекта выполните:
   ```bash
   docker compose up --build
   ```
3. Откройте в браузере:
   - Frontend: http://localhost:8080
   - Backend health: http://localhost:8080/api/health

## API (через Nginx)
- `POST /api/upload` (multipart/form-data, поле `file`)
- `GET /api/images?page=1&per_page=50`
- `DELETE /api/images/<id>`
- `GET /api/random`
- Изображения доступны по `GET /images/<filename>`

## Замечания по безопасности
- Ограничение размера загрузки: 5 MB (и на Flask, и на Nginx).
- Разрешённые расширения: jpg/jpeg/png/gif.
- Для продакшена рекомендуется добавить:
  - антивирус/контент-сканирование,
  - строгую MIME-проверку на стороне backend,
  - rate-limit на `/api/upload`,
  - отдельный storage (S3/MinIO) вместо локального volume.
