# =============================================================================
# search.py
# =============================================================================
# Implementação dos quatro algoritmos de procura em grafos pedidos no trabalho:
#
#   PROCURA CEGA (sem conhecimento sobre o objetivo):
#     1. Custo Uniforme  — garante caminho ótimo; expande pelo menor g(n)
#     2. Profundidade Limitada — DFS com teto de profundidade; não garante óptimo
#
#   PROCURA INFORMADA / HEURÍSTICA (usa estimativa do custo restante):
#     3. Sôfrega (Greedy) — rápida mas não garante óptimo; expande pelo menor h(n)
#     4. A*               — garante óptimo com heurística admissível; f(n)=g(n)+h(n)
#
# Todos os algoritmos devolvem um triplo:
#   (path, cost, iterations)
#   - path       : lista de cidades do caminho encontrado (ou None se falhou)
#   - cost       : custo total em km (ou inf se falhou)
#   - iterations : histórico passo a passo, usado para mostrar o processo ao utilizador
#
# Estrutura interna comum:
#   - frontier : fila de prioridade (heap) com os nós por expandir
#   - explored : conjunto de nós já expandidos (para não revisitar)
# =============================================================================

import heapq
import itertools

# Contador global de desempate para a fila de prioridade (heap).
# O Python compara tuplos elemento a elemento; se dois nós têm o mesmo custo,
# tentaria comparar as listas de caminho (que não são comparáveis entre si).
# Inserir um inteiro único como segundo elemento do tuplo evita esse erro,
# pois o Python nunca chegará a comparar o terceiro elemento (a lista).
_counter = itertools.count()


# ---------------------------------------------------------------------------
# 1. Custo Uniforme
# ---------------------------------------------------------------------------
# Ideia: expandir sempre o nó com menor custo acumulado g(n) desde a origem.
# Usa uma fila de prioridade (min-heap) ordenada por g(n).
# É completo e óptimo quando os custos das arestas são positivos.
# Equivalente ao algoritmo de Dijkstra para grafos com custos positivos.

def uniform_cost_search(graph: dict, start: str, goal: str):
    """
    Procura de Custo Uniforme (UCS).
    Expande sempre o nó com menor custo acumulado g(n).

    Parâmetros:
        graph : dicionário de adjacências { cidade: { vizinho: custo } }
        start : cidade de origem
        goal  : cidade de destino

    Retorna:
        path      : lista de cidades do caminho encontrado (ou None)
        cost      : custo total do caminho
        iterations: lista de dicionários com o estado em cada iteração
    """
    # Cada entrada do heap é o tuplo (g, id_unico, caminho).
    # g        = custo acumulado desde a origem até ao nó atual
    # id_unico = contador de desempate (ver nota sobre _counter acima)
    # caminho  = lista de cidades percorridas até ao nó atual
    frontier = [(0, next(_counter), [start])]

    # Conjunto de nós já expandidos. Quando um nó é retirado do heap e já
    # está em explored, é descartado (pode ter entrado várias vezes com
    # custos diferentes antes de ser pela primeira vez expandido).
    explored = set()

    # Registo de cada nó expandido, guardando o estado nesse momento.
    # Será apresentado ao utilizador para mostrar o funcionamento do algoritmo.
    iterations = []

    while frontier:
        # Retirar o nó com menor custo acumulado da fila de prioridade
        cost, _, path = heapq.heappop(frontier)
        node = path[-1]  # cidade atual = último elemento do caminho

        # Se este nó já foi expandido com um custo menor, ignorar esta entrada
        if node in explored:
            continue

        # Registar esta expansão no histórico de iterações
        iterations.append({
            'node': node,
            'g':    cost,   # g(n): custo real acumulado desde a origem
            'path': list(path),
        })

        # Verificar se chegámos ao destino
        if node == goal:
            return path, cost, iterations

        # Marcar como expandido para não revisitar
        explored.add(node)

        # Expandir todos os vizinhos ainda não visitados
        for neighbor, edge_cost in sorted(graph.get(node, {}).items()):
            if neighbor not in explored:
                # Inserir vizinho na fila com o novo custo acumulado
                heapq.heappush(frontier, (
                    cost + edge_cost,
                    next(_counter),
                    path + [neighbor],
                ))

    # Fila vazia: não existe caminho entre start e goal
    return None, float('inf'), iterations


# ---------------------------------------------------------------------------
# 2. Profundidade Limitada
# ---------------------------------------------------------------------------
# Ideia: DFS (Depth-First Search) com um limite máximo de profundidade.
# Evita ficar preso em caminhos infinitos (ciclos), mas pode não encontrar
# a solução se o limite for demasiado baixo.
# NÃO garante o caminho ótimo — depende da ordem de exploração dos vizinhos.

def depth_limited_search(graph: dict, start: str, goal: str, limit: int):
    """
    Procura em Profundidade Limitada (DLS).
    DFS com limite máximo de profundidade.

    Parâmetros:
        graph : dicionário de adjacências
        start : cidade de origem
        goal  : cidade de destino
        limit : profundidade máxima permitida (número de arestas a percorrer)

    Retorna:
        path      : lista de cidades do caminho encontrado (ou None)
        cost      : custo total do caminho
        iterations: lista de dicionários com o estado em cada iteração
    """
    iterations = []

    def _dls(node, path, cost, depth):
        """
        Função recursiva interna.
        node  : cidade atual
        path  : caminho percorrido até agora (incluindo node)
        cost  : custo acumulado até node
        depth : "combustível" restante — quantas arestas ainda podemos percorrer
        """
        iterations.append({
            'node':  node,
            'depth': limit - depth,  # profundidade atual (0 = origem)
            'g':     cost,
            'path':  list(path),
        })

        # Caso base 1: chegámos ao destino
        if node == goal:
            return path, cost

        # Caso base 2: atingimos o limite de profundidade, parar este ramo
        if depth == 0:
            return None, None

        # Expandir vizinhos em ordem alfabética (para resultados determinísticos)
        for neighbor, edge_cost in sorted(graph.get(node, {}).items()):
            if neighbor not in path:  # evitar ciclos: não voltar a cidades já no caminho atual
                result_path, result_cost = _dls(
                    neighbor,
                    path + [neighbor],   # novo caminho com o vizinho incluído
                    cost + edge_cost,
                    depth - 1,           # consumir uma unidade de profundidade
                )
                # Se encontrou solução neste ramo, propagar para cima
                if result_path is not None:
                    return result_path, result_cost

        # Nenhum vizinho levou ao objetivo — falha neste ramo
        return None, None

    # Iniciar DLS a partir da origem com o limite definido
    result_path, result_cost = _dls(start, [start], 0, limit)
    return result_path, (result_cost if result_cost is not None else float('inf')), iterations


# ---------------------------------------------------------------------------
# 3. Procura Sôfrega (Greedy Best-First)
# ---------------------------------------------------------------------------
# Ideia: expandir sempre o nó que parece estar "mais perto" do objetivo,
# de acordo com a heurística h(n). Ignora completamente o custo já percorrido.
# É geralmente mais rápida que UCS/A*, mas NÃO garante o caminho ótimo.
# Pode ser "enganada" por heurísticas que levam a becos sem saída.

def greedy_search(graph: dict, start: str, goal: str, heuristic):
    """
    Procura Sôfrega (Greedy Best-First Search).
    Expande o nó com menor valor heurístico h(n).

    Parâmetros:
        graph     : dicionário de adjacências
        start     : cidade de origem
        goal      : cidade de destino
        heuristic : função  h(cidade) -> int  — estimativa do custo até ao destino

    Retorna:
        path      : lista de cidades do caminho encontrado (ou None)
        cost      : custo real total do caminho
        iterations: lista de dicionários com o estado em cada iteração
    """
    # Heap ordenado por h(n). Guardamos também o custo real g para exibição,
    # mas ele NÃO influencia a ordem de expansão neste algoritmo.
    # Tuplo: (h, id_unico, caminho, g_acumulado)
    frontier = [(heuristic(start), next(_counter), [start], 0)]
    explored = set()
    iterations = []

    while frontier:
        # Retirar o nó com menor heurística
        h_val, _, path, cost = heapq.heappop(frontier)
        node = path[-1]

        if node in explored:
            continue

        iterations.append({
            'node': node,
            'h':    h_val,  # h(n): estimativa do custo restante até ao destino
            'g':    cost,   # g(n): custo real percorrido (apenas para exibição)
            'path': list(path),
        })

        if node == goal:
            return path, cost, iterations

        explored.add(node)

        for neighbor, edge_cost in sorted(graph.get(node, {}).items()):
            if neighbor not in explored:
                heapq.heappush(frontier, (
                    heuristic(neighbor),      # prioridade = apenas h(vizinho)
                    next(_counter),
                    path + [neighbor],
                    cost + edge_cost,
                ))

    return None, float('inf'), iterations


# ---------------------------------------------------------------------------
# 4. A*
# ---------------------------------------------------------------------------
# Ideia: combinar o custo real já percorrido g(n) com a estimativa do custo
# restante h(n), usando f(n) = g(n) + h(n) como critério de expansão.
# É completo e óptimo quando a heurística é admissível (nunca sobrestima).
# Equilibra exploração (UCS) e foco no objetivo (Sôfrega).

def a_star_search(graph: dict, start: str, goal: str, heuristic):
    """
    Procura A*.
    Expande o nó com menor f(n) = g(n) + h(n).

    Parâmetros:
        graph     : dicionário de adjacências
        start     : cidade de origem
        goal      : cidade de destino
        heuristic : função  h(cidade) -> int  — estimativa admissível do custo restante

    Retorna:
        path      : lista de cidades do caminho encontrado (ou None)
        cost      : custo real total do caminho (g do nó objetivo)
        iterations: lista de dicionários com o estado em cada iteração
    """
    h0 = heuristic(start)  # heurística do nó inicial
    # Heap ordenado por f(n) = g(n) + h(n).
    # Tuplo: (f, id_unico, g_acumulado, caminho)
    frontier = [(h0, next(_counter), 0, [start])]
    explored = set()
    iterations = []

    while frontier:
        # Retirar o nó com menor f = g + h
        f_val, _, g_cost, path = heapq.heappop(frontier)
        node = path[-1]

        if node in explored:
            continue

        # Recuperar h(n) a partir de f e g para exibição na tabela de iterações
        h_val = f_val - g_cost  # h = f - g

        iterations.append({
            'node': node,
            'f':    f_val,   # f(n) = g(n) + h(n): custo total estimado
            'g':    g_cost,  # g(n): custo real desde a origem
            'h':    h_val,   # h(n): estimativa do custo restante
            'path': list(path),
        })

        if node == goal:
            return path, g_cost, iterations

        explored.add(node)

        for neighbor, edge_cost in sorted(graph.get(node, {}).items()):
            if neighbor not in explored:
                new_g = g_cost + edge_cost
                new_h = heuristic(neighbor)
                # f do vizinho: custo real até ele + estimativa dali ao destino
                heapq.heappush(frontier, (
                    new_g + new_h,
                    next(_counter),
                    new_g,
                    path + [neighbor],
                ))

    # Heap vazio: não existe caminho entre start e goal
    return None, float('inf'), iterations
