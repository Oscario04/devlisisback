# Devlisis Backend API

Backend corporativo para recepción de leads desde la landing de Devlisis.

## Stack

- Python 3.12
- FastAPI
- Pydantic V2
- MongoDB
- PyMongo
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
```

## Variables de entorno

1. Copiar `.env.example` a `.env`.
2. Configurar `MONGODB_URI` y `MONGODB_DB_NAME`.
2. Completar credenciales SMTP.

## Ejecución local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Endpoints

- `GET /health`
- `POST /api/contact`
- `GET /api/contact` (pendiente de proteger con JWT)

## Docs

- Swagger: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
