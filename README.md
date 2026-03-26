Repository for the Final Project of the Artificial Intelligence Curricular Unit.

## Authors
David Borges

Patricia Oliveira

Susana Tavares

<<<<<<< HEAD
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
=======

## How to run

1. Install dependencies:

	pip install -r requirements.txt

2. Start the app:

	python src/main.py

3. Optional validation (recommended before delivery):

	python src/self_check.py


## What the validation checks

- Graph consistency (bidirectional edges and positive distances)
- Heuristic quality for Faro (admissibility and consistency)
- Cost optimality comparison between UCS and A*
- Path integrity (path cost matches reported algorithm cost)
>>>>>>> 082d84687450d948b8000e048e122509aa98880b
