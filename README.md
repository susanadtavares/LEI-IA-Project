Repository for the Final Project of the Artificial Intelligence Curricular Unit.

## Authors
David Borges

Patricia Oliveira

Susana Tavares

## Website Implementation (FastAPI + React)

This project now includes a web version with:

- Backend API in `backend/` using FastAPI
- Frontend in `frontend/` using React + Vite
- Legacy AI logic reused from `backend/src/` (search, OCR, LLM)

### Project Structure

- `backend/src/`: original terminal modules (graph, search, OCR, LLM)
- `backend/app/main.py`: API routes
- `backend/app/services.py`: bridge to legacy AI modules
- `frontend/src/App.jsx`: web UI workflow
- `frontend/src/api.js`: API client

### Backend Setup

From project root (Windows PowerShell):

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

API will run at `http://localhost:8000`.

If PowerShell blocks script activation, use CMD and run:

```bat
.\.venv\Scripts\activate.bat
```

### Frontend Setup

From project root (new terminal):

```bash
cd frontend
copy .env.example .env
npm.cmd install
npm.cmd run dev
```

Frontend will run at `http://localhost:5173` and call the backend at `http://localhost:8000`.

### Main API Endpoints

- `GET /health`
- `GET /cities`
- `GET /models`
- `POST /auth/plate`
- `POST /auth/plate-ocr`
- `POST /route`
- `POST /route/compare`
- `POST /attractions`

Swagger docs available at `http://localhost:8000/docs`.
