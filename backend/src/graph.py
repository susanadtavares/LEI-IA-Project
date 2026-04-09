# =============================================================================
# graph.py
# =============================================================================
# Este ficheiro define a estrutura de dados central do programa:
#   - GRAPH     : grafo bidirecional com as cidades Portuguesas e distâncias
#                 reais (quilómetros de estrada) entre cidades vizinhas.
#   - HEURISTIC_FARO : tabela de distâncias em linha reta de cada cidade até
#                 Faro, usada como heurística nos algoritmos A* e Sôfrega.
#   - CITIES    : lista ordenada alfabeticamente de todas as cidades.
#   - get_heuristic() : função que devolve a heurística adequada ao destino.
#
# Nota: todas as ligações são bidirecionais, ou seja, se A liga a B com custo X,
# então B também liga a A com o mesmo custo X. Por isso cada aresta foi
# inserida nos dois sentidos no dicionário GRAPH.
# =============================================================================

import math

# -----------------------------------------------------------------------------
# Grafo de adjacências
# -----------------------------------------------------------------------------
# Estrutura: { cidade: { vizinho: distância_em_km, ... }, ... }
# Cada entrada representa as cidades diretamente ligadas por estrada e a
# distância real (em km) entre elas, retirada do enunciado do trabalho.
GRAPH = {
    'Aveiro':         {'Porto': 68,   'Viseu': 95,  'Coimbra': 68,  'Leiria': 115},
    'Braga':          {'Viana do Castelo': 48, 'Vila Real': 106, 'Porto': 53},
    'Bragança':       {'Vila Real': 137, 'Guarda': 202},
    'Beja':           {'Évora': 78,   'Faro': 152,  'Setúbal': 142},
    'Castelo Branco': {'Coimbra': 159,'Guarda': 106, 'Portalegre': 80, 'Évora': 203},
    'Coimbra':        {'Aveiro': 68,  'Viseu': 96,  'Leiria': 67,   'Castelo Branco': 159},
    'Évora':          {'Lisboa': 150, 'Santarém': 117, 'Portalegre': 131, 'Setúbal': 103, 'Beja': 78, 'Castelo Branco': 203},
    'Faro':           {'Setúbal': 249,'Lisboa': 299, 'Beja': 152},
    'Guarda':         {'Vila Real': 157, 'Viseu': 85, 'Bragança': 202, 'Castelo Branco': 106},
    'Leiria':         {'Lisboa': 129, 'Santarém': 70, 'Aveiro': 115, 'Coimbra': 67},
    'Lisboa':         {'Santarém': 78,'Setúbal': 50, 'Leiria': 129,  'Faro': 299,  'Évora': 150},
    'Portalegre':     {'Castelo Branco': 80, 'Évora': 131},
    'Porto':          {'Aveiro': 68,  'Braga': 53,  'Viana do Castelo': 71, 'Vila Real': 116, 'Viseu': 133},
    'Santarém':       {'Leiria': 70,  'Lisboa': 78, 'Évora': 117},
    'Setúbal':        {'Lisboa': 50,  'Évora': 103, 'Beja': 142,    'Faro': 249},
    'Viana do Castelo': {'Braga': 48, 'Porto': 71},
    'Vila Real':      {'Braga': 106,  'Bragança': 137, 'Guarda': 157, 'Porto': 116, 'Viseu': 110},
    'Viseu':          {'Aveiro': 95,  'Coimbra': 96, 'Guarda': 85,   'Porto': 133, 'Vila Real': 110},
}

# -----------------------------------------------------------------------------
# Heurística admissível: distância em linha reta até Faro (km)
# -----------------------------------------------------------------------------
# Para os algoritmos de procura informada (A* e Sôfrega) é necessária uma
# heurística h(n) que estime o custo restante de um nó n até ao objetivo.
#
# Uma heurística é ADMISSÍVEL se nunca sobrestima o custo real, o que é
# garantido pela distância em linha reta (que é sempre <= distância real).
# Isso assegura que o A* encontra SEMPRE o caminho ótimo.
#
# Estes valores foram fornecidos diretamente no enunciado (Tabela 2) e
# correspondem à distância a Faro; por isso a heurística só é usada quando
# o destino escolhido pelo utilizador é Faro.
HEURISTIC_FARO = {
    'Aveiro':           366,
    'Braga':            454,
    'Bragança':         487,
    'Beja':             99,
    'Castelo Branco':   280,
    'Coimbra':          319,
    'Évora':            157,
    'Faro':             0,
    'Guarda':           352,
    'Leiria':           278,
    'Lisboa':           195,
    'Portalegre':       228,
    'Porto':            418,
    'Santarém':         231,
    'Setúbal':          168,
    'Viana do Castelo': 473,
    'Vila Real':        429,
    'Viseu':            363,
}

# -----------------------------------------------------------------------------
# Coordenadas aproximadas (latitude, longitude) das cidades
# -----------------------------------------------------------------------------
# Usadas para estimar a distancia em linha reta entre qualquer par de cidades.
# Para o objetivo Faro continuamos a usar a tabela oficial do enunciado.
CITY_COORDS = {
    'Aveiro': (40.6405, -8.6538),
    'Braga': (41.5454, -8.4265),
    'Bragança': (41.8060, -6.7567),
    'Beja': (38.0151, -7.8632),
    'Castelo Branco': (39.8222, -7.4909),
    'Coimbra': (40.2033, -8.4103),
    'Évora': (38.5710, -7.9135),
    'Faro': (37.0194, -7.9304),
    'Guarda': (40.5373, -7.2677),
    'Leiria': (39.7444, -8.8072),
    'Lisboa': (38.7223, -9.1393),
    'Portalegre': (39.2967, -7.4280),
    'Porto': (41.1579, -8.6291),
    'Santarém': (39.2362, -8.6869),
    'Setúbal': (38.5244, -8.8882),
    'Viana do Castelo': (41.6918, -8.8345),
    'Vila Real': (41.3006, -7.7441),
    'Viseu': (40.6610, -7.9097),
}

# Lista de todas as cidades disponíveis no grafo, ordenada alfabeticamente.
# Usada nos menus de seleção de origem/destino.
CITIES = sorted(GRAPH.keys())


def _haversine_km(city_a: str, city_b: str) -> float:
    """
    Distancia geodesica aproximada entre duas cidades (km) usando Haversine.
    """
    coords_a = CITY_COORDS.get(city_a)
    coords_b = CITY_COORDS.get(city_b)
    if not coords_a or not coords_b:
        return 0.0

    lat1, lon1 = coords_a
    lat2, lon2 = coords_b

    radius_km = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_km * c


def get_heuristic(goal: str):
    """
    Devolve a função heurística adequada para o destino escolhido.

        Quando o destino é Faro, usa a tabela oficial do enunciado.
        Para outros destinos, usa a distancia geodesica em linha reta aproximada
        com base em coordenadas (Haversine), tornando A* e Sôfrega informados em
        todo o espaço de estados.

    Parâmetros:
        goal : nome da cidade destino

    Retorna:
        Função  h(node) -> int  que recebe um nome de cidade e devolve a
        estimativa do custo restante até ao destino.
    """
    if goal == 'Faro':
        # Quando o destino é Faro, usamos a tabela em linha reta fornecida.
        # .get(node, float('inf')) garante que cidades desconhecidas não
        # causam KeyError e são tratadas como inatingíveis.
        return lambda node: HEURISTIC_FARO.get(node, float('inf'))
    else:
        return lambda node: _haversine_km(node, goal)
