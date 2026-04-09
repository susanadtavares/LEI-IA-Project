Repository for the Final Project of the Artificial Intelligence Curricular Unit.

## Authors
David Borges

Patricia Oliveira

Susana Tavares

## Project Overview

The project implements a Portuguese city route planner using AI search methods:

- Uniform Cost Search (UCS)
- Depth-Limited Search (DLS)
- Greedy Best-First Search
- A*

It also includes:

- OCR-based login with Portuguese license plate recognition
- Local LLM integration (Ollama) for city attractions
- Web product version with FastAPI (backend) + React (frontend)
- Command-line version in `backend/src/main.py`

## Project Structure

- `backend/src/`: search logic, graph model, OCR, LLM, validation scripts
- `backend/app/`: FastAPI API, schemas, service layer
- `frontend/`: React + Vite web interface

## Running the Web Version

### 1. Backend (FastAPI)

From project root:

```bash
python -m venv .venv
.\.venv\Scripts\activate.bat
cd backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend URL: `http://localhost:8000`
Swagger docs: `http://localhost:8000/docs`

### 2. Frontend (React + Vite)

From project root in another terminal:

```bash
cd frontend
npm.cmd install
npm.cmd run dev
```

Frontend URL: `http://localhost:5173`

## Running the CLI Version

From project root:

```bash
cd backend\src
python main.py
```

## Validation Before Delivery

Run the automatic consistency check:

```bash
cd backend\src
python self_check.py
```

The validator checks:

- Graph symmetry and positive edge costs
- Heuristic admissibility and consistency for all goals
- A* optimality vs UCS across origin-destination pairs
- Path integrity (reported cost matches path edge sum)

## Main API Endpoints

- `GET /health`
- `GET /cities`
- `GET /models`
- `POST /auth/plate`
- `POST /auth/plate-ocr`
- `POST /route`
- `POST /route/compare`
- `POST /attractions`
