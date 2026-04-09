# LEI-IA Frontend

Web interface for the IA practical project.

## Features

- Login with Portuguese plate validation (manual or OCR upload)
- Route execution with four algorithms: UCS, DLS, Greedy, A*
- Iteration table adapted to each algorithm
- Route metrics (execution time, expanded nodes, path nodes)
- Side-by-side comparison of all algorithms
- Export comparison results to JSON and CSV
- LLM attractions per city in the selected route

## Prerequisites

- Node.js 18+
- Backend API running on `http://localhost:8000`

## Run

From the project root:

```bash
cd frontend
npm.cmd install
npm.cmd run dev
```

Open `http://localhost:5173`.

## Build

```bash
npm.cmd run build
npm.cmd run preview
```

## API Base URL

Default API URL is `http://localhost:8000`.

To override, define in `.env`:

```bash
VITE_API_BASE=http://localhost:8000
```
