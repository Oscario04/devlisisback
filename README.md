# Devlisis Backend API

Backend corporativo para recepción de leads desde la landing de Devlisis.

## Stack

- Python 3.12
- FastAPI
- Pydantic V2
- SQLAlchemy 2
- SQLite
- Alembic
- Uvicorn
- python-dotenv

## Estructura

```text
app/
  api/
  services/
  schemas/
  models/
  repositories/
  core/
  database/
  utils/
  main.py
alembic/
```

## Variables de entorno

1. Copiar `.env.example` a `.env`.
2. Completar credenciales SMTP.

## Ejecución local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Migraciones

```bash
alembic upgrade head
```

> La app también crea tablas en startup para facilitar la primera ejecución local.

## Endpoints

- `GET /health`
- `POST /api/contact`
- `GET /api/contact` (pendiente de proteger con JWT)

## Docs

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
