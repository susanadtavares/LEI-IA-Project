# pyright: reportMissingImports=false

import os
import re
import sys
import importlib
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
LEGACY_SRC = PROJECT_ROOT / "backend" / "src"
if not LEGACY_SRC.exists():
    # Backward compatibility if modules are still in the old root src folder
    LEGACY_SRC = PROJECT_ROOT / "src"

if str(LEGACY_SRC) not in sys.path:
    sys.path.insert(0, str(LEGACY_SRC))

graph = importlib.import_module("graph")
llm = importlib.import_module("llm")
ocr = importlib.import_module("ocr")
search = importlib.import_module("search")

CITIES = graph.CITIES
GRAPH = graph.GRAPH
get_heuristic = graph.get_heuristic

DEFAULT_MODEL = llm.DEFAULT_MODEL
get_city_attractions = llm.get_city_attractions
list_available_models = llm.list_available_models

read_plate_from_image = ocr.read_plate_from_image

a_star_search = search.a_star_search
depth_limited_search = search.depth_limited_search
greedy_search = search.greedy_search
uniform_cost_search = search.uniform_cost_search


PLATE_PATTERN = re.compile(r"^[A-Z0-9]{2}-[A-Z0-9]{2}-[A-Z0-9]{2}$")


def get_cities() -> list[str]:
    return list(CITIES)


def normalize_plate(plate: str) -> str:
    clean = re.sub(r"[-\s]", "", plate).upper()
    if len(clean) != 6:
        raise ValueError("Matrícula inválida. Usa formato tipo AA-00-BB")
    normalized = f"{clean[0:2]}-{clean[2:4]}-{clean[4:6]}"
    if not PLATE_PATTERN.match(normalized):
        raise ValueError("Matrícula inválida. Usa formato tipo AA-00-BB")
    return normalized


def run_route(start: str, goal: str, algorithm: str, depth_limit: int | None = None):
    if start not in CITIES or goal not in CITIES:
        raise ValueError("Cidade inválida")
    if start == goal:
        raise ValueError("Origem e destino não podem ser iguais")

    heuristic = get_heuristic(goal)

    if algorithm == "ucs":
        path, cost, iterations = uniform_cost_search(GRAPH, start, goal)
    elif algorithm == "dls":
        if depth_limit is None:
            raise ValueError("depth_limit é obrigatório para dls")
        path, cost, iterations = depth_limited_search(GRAPH, start, goal, depth_limit)
    elif algorithm == "greedy":
        path, cost, iterations = greedy_search(GRAPH, start, goal, heuristic)
    elif algorithm == "astar":
        path, cost, iterations = a_star_search(GRAPH, start, goal, heuristic)
    else:
        raise ValueError("Algoritmo inválido. Usa ucs|dls|greedy|astar")

    return {
        "algorithm": algorithm,
        "path": path,
        "cost": cost,
        "iterations": iterations,
    }


def run_compare(start: str, goal: str, depth_limit: int):
    return [
        run_route(start, goal, "ucs"),
        run_route(start, goal, "dls", depth_limit),
        run_route(start, goal, "greedy"),
        run_route(start, goal, "astar"),
    ]


def read_plate_upload(temp_path: str):
    return read_plate_from_image(temp_path)


def get_attractions(city: str, model: str | None):
    chosen_model = model or DEFAULT_MODEL
    result = get_city_attractions(city, chosen_model)
    return {"city": city, "model": chosen_model, "content": result}


def get_models() -> list[str]:
    return list_available_models()
