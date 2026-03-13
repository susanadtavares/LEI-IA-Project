# search.py
# Implementação dos quatro algoritmos de procura:
#   1. Custo Uniforme (Uniform Cost Search - UCS)
#   2. Profundidade Limitada (Depth-Limited Search - DLS)
#   3. Procura Sôfrega (Greedy Best-First Search)
#   4. A* (A-Star)

import heapq
import itertools

# Contador global para desempate em heaps (evita comparação de listas)
_counter = itertools.count()


# ---------------------------------------------------------------------------
# 1. Custo Uniforme
# ---------------------------------------------------------------------------

def uniform_cost_search(graph: dict, start: str, goal: str):
    """
    Procura de Custo Uniforme (UCS).
    Expande sempre o nó com menor custo acumulado g(n).

    Retorna:
        path      : lista de cidades do caminho encontrado (ou None)
        cost      : custo total do caminho
        iterations: lista de dicionários com o estado em cada iteração
    """
    # (custo, id, caminho)
    frontier = [(0, next(_counter), [start])]
    explored = set()
    iterations = []

    while frontier:
        cost, _, path = heapq.heappop(frontier)
        node = path[-1]

        if node in explored:
            continue

        iterations.append({
            'node': node,
            'g':    cost,
            'path': list(path),
        })

        if node == goal:
            return path, cost, iterations

        explored.add(node)

        for neighbor, edge_cost in sorted(graph.get(node, {}).items()):
            if neighbor not in explored:
                heapq.heappush(frontier, (
                    cost + edge_cost,
                    next(_counter),
                    path + [neighbor],
                ))

    return None, float('inf'), iterations


# ---------------------------------------------------------------------------
# 2. Profundidade Limitada
# ---------------------------------------------------------------------------

def depth_limited_search(graph: dict, start: str, goal: str, limit: int):
    """
    Procura em Profundidade Limitada (DLS).
    DFS com limite máximo de profundidade.

    Retorna:
        path      : lista de cidades do caminho encontrado (ou None)
        cost      : custo total do caminho
        iterations: lista de dicionários com o estado em cada iteração
    """
    iterations = []

    def _dls(node, path, cost, depth):
        iterations.append({
            'node':  node,
            'depth': limit - depth,
            'g':     cost,
            'path':  list(path),
        })

        if node == goal:
            return path, cost

        if depth == 0:
            return None, None

        for neighbor, edge_cost in sorted(graph.get(node, {}).items()):
            if neighbor not in path:          # evitar ciclos
                result_path, result_cost = _dls(
                    neighbor,
                    path + [neighbor],
                    cost + edge_cost,
                    depth - 1,
                )
                if result_path is not None:
                    return result_path, result_cost

        return None, None

    result_path, result_cost = _dls(start, [start], 0, limit)
    return result_path, (result_cost if result_cost is not None else float('inf')), iterations


# ---------------------------------------------------------------------------
# 3. Procura Sôfrega (Greedy Best-First)
# ---------------------------------------------------------------------------

def greedy_search(graph: dict, start: str, goal: str, heuristic):
    """
    Procura Sôfrega (Greedy Best-First Search).
    Expande o nó com menor valor heurístico h(n).

    heuristic: função que recebe um nome de cidade e devolve o valor h.

    Retorna:
        path      : lista de cidades do caminho encontrado (ou None)
        cost      : custo real total do caminho
        iterations: lista de dicionários com o estado em cada iteração
    """
    frontier = [(heuristic(start), next(_counter), [start], 0)]
    explored = set()
    iterations = []

    while frontier:
        h_val, _, path, cost = heapq.heappop(frontier)
        node = path[-1]

        if node in explored:
            continue

        iterations.append({
            'node': node,
            'h':    h_val,
            'g':    cost,
            'path': list(path),
        })

        if node == goal:
            return path, cost, iterations

        explored.add(node)

        for neighbor, edge_cost in sorted(graph.get(node, {}).items()):
            if neighbor not in explored:
                heapq.heappush(frontier, (
                    heuristic(neighbor),
                    next(_counter),
                    path + [neighbor],
                    cost + edge_cost,
                ))

    return None, float('inf'), iterations


# ---------------------------------------------------------------------------
# 4. A*
# ---------------------------------------------------------------------------

def a_star_search(graph: dict, start: str, goal: str, heuristic):
    """
    Procura A*.
    Expande o nó com menor f(n) = g(n) + h(n).

    heuristic: função que recebe um nome de cidade e devolve o valor h.

    Retorna:
        path      : lista de cidades do caminho encontrado (ou None)
        cost      : custo real total do caminho (g do nó objetivo)
        iterations: lista de dicionários com o estado em cada iteração
    """
    h0 = heuristic(start)
    frontier = [(h0, next(_counter), 0, [start])]   # (f, id, g, path)
    explored = set()
    iterations = []

    while frontier:
        f_val, _, g_cost, path = heapq.heappop(frontier)
        node = path[-1]

        if node in explored:
            continue

        h_val = f_val - g_cost
        iterations.append({
            'node': node,
            'f':    f_val,
            'g':    g_cost,
            'h':    h_val,
            'path': list(path),
        })

        if node == goal:
            return path, g_cost, iterations

        explored.add(node)

        for neighbor, edge_cost in sorted(graph.get(node, {}).items()):
            if neighbor not in explored:
                new_g = g_cost + edge_cost
                new_h = heuristic(neighbor)
                heapq.heappush(frontier, (
                    new_g + new_h,
                    next(_counter),
                    new_g,
                    path + [neighbor],
                ))

    return None, float('inf'), iterations
