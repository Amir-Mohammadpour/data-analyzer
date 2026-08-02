# AI-Powered Data Analyzer API

A FastAPI backend that lets users upload CSV files and ask natural-language questions about their data, powered by an LLM.

Upload a dataset → the API profiles it with Pandas → ask questions in plain English → get AI-generated answers grounded in the actual data.

## Features

- **JWT authentication** — register/login with hashed passwords (bcrypt) and access tokens
- **CSV upload & processing** — async file upload with validation, size limits, and automatic profiling (row/column counts, types, missing values)
- **AI-powered Q&A** — ask questions about a dataset; the LLM answers using a statistical summary of the data, not the raw file
- **Conversation history** — every question and answer is stored per dataset
- **Async throughout** — FastAPI + async SQLAlchemy + asyncpg for non-blocking I/O
- **Dockerized** — full stack (API + PostgreSQL) runs with one command

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL + async SQLAlchemy 2.0 |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (python-jose) + passlib/bcrypt |
| Data processing | Pandas |
| AI | OpenAI-compatible API (works with OpenAI, etc.) |
| Containerization | Docker + Docker Compose |

## Project Structure

```
app/
├── main.py             # FastAPI app, CORS, lifespan
├── config.py            # Environment-based settings
├── database.py           # Async engine & session
├── models/                # SQLAlchemy models
├── schemas/                # Pydantic request/response schemas
├── core/                    # Security & auth dependencies
├── services/                  # File handling, Pandas profiling, AI calls
└── routers/                    # API endpoints
alembic/                          # Database migrations
Dockerfile
docker-compose.yml
```

## Getting Started

### Prerequisites
- Docker & Docker Compose
- An API key from an OpenAI-compatible provider (e.g., [OpenAI](https://platform.openai.com) or the free [Google Gemini API](https://aistudio.google.com/apikey))

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/<Amir-Mohammadpour>/data-analyzer.git
   cd data-analyzer
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Fill in `SECRET_KEY`, `OPENAI_API_KEY`, and `POSTGRES_*` values in `.env`.

3. **Start the stack**
   ```bash
   docker compose up --build
   ```

4. **Run database migrations** (in a new terminal, while the stack is running)
   ```bash
   docker compose exec api alembic upgrade head
   ```

5. **Explore the API**
   Open [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger docs.

### Running without Docker

```bash
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```
(Requires a local PostgreSQL instance and a matching `DATABASE_URL` in `.env`.)

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Create a new user account |
| POST | `/api/v1/auth/login` | Get a JWT access token |
| POST | `/api/v1/datasets/upload` | Upload and process a CSV file |
| GET | `/api/v1/datasets` | List the current user's datasets |
| GET | `/api/v1/datasets/{id}` | Get details of a specific dataset |
| POST | `/api/v1/datasets/{id}/conversations` | Ask a question about a dataset |
| GET | `/api/v1/datasets/{id}/conversations` | Get question/answer history |
| GET | `/health` | Health check |

All endpoints except `/auth/*` and `/health` require a `Bearer` token in the `Authorization` header.

## Environment Variables

See `.env.example` for the full list. Key variables:

| Variable | Description |
|---|---|
| `DATABASE_URL` | Async PostgreSQL connection string |
| `SECRET_KEY` | Secret used to sign JWTs |
| `OPENAI_API_KEY` | API key for the LLM provider |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiration time |

## Possible Future Improvements

- Refresh tokens (currently access-token-only by design, for simplicity)
- Rate limiting on the login endpoint
- Cloud storage (S3) instead of local disk for uploaded files
- Automated test suite (pytest)

