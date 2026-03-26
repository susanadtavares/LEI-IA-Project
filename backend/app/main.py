import os
import tempfile

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .schemas import AttractionsRequest, CompareRequest, ManualPlateRequest, RouteRequest
from .services import (
    get_attractions,
    get_cities,
    get_models,
    normalize_plate,
    read_plate_upload,
    run_compare,
    run_route,
)

app = FastAPI(title="LEI-IA Project API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/cities")
def cities():
    return {"cities": get_cities()}


@app.get("/models")
def models():
    return {"models": get_models()}


@app.post("/auth/plate")
def auth_plate(payload: ManualPlateRequest):
    try:
        normalized = normalize_plate(payload.plate)
        return {"plate": normalized, "valid": True}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/auth/plate-ocr")
async def auth_plate_ocr(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "")[1] or ".jpg"
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        plate = read_plate_upload(tmp_path)
        if not plate:
            raise HTTPException(status_code=422, detail="Não foi possível reconhecer matrícula")
        return {"plate": plate, "valid": True}
    except HTTPException:
        raise
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ImportError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erro inesperado OCR: {exc}") from exc
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/route")
def route(payload: RouteRequest):
    try:
        return run_route(payload.start, payload.goal, payload.algorithm, payload.depth_limit)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/route/compare")
def compare(payload: CompareRequest):
    try:
        return {"results": run_compare(payload.start, payload.goal, payload.depth_limit)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/attractions")
def attractions(payload: AttractionsRequest):
    return get_attractions(payload.city, payload.model)
