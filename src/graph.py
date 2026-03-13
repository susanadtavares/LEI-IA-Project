# graph.py
# Grafo de cidades Portuguesas com distâncias quilométricas (bidireccional)

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

# Heurística: distância em linha reta de cada cidade até Faro (km)
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

CITIES = sorted(GRAPH.keys())


def get_heuristic(goal: str):
    """
    Devolve a função heurística para um dado destino.
    A tabela fornecida é apenas para Faro; para outros destinos retorna 0.
    """
    if goal == 'Faro':
        return lambda node: HEURISTIC_FARO.get(node, float('inf'))
    else:
        # Sem heurística definida: retorna 0 (A* degrada para UCS, Sôfrega para BFS)
        return lambda node: 0
