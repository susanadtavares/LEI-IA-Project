"""
self_check.py
Validação automática do projeto (grafo, heurística e algoritmos de procura).
"""

from graph import GRAPH, CITIES, HEURISTIC_FARO, get_heuristic
from search import uniform_cost_search, a_star_search, greedy_search, path_cost


def validate_graph_symmetry(graph: dict) -> list[str]:
    issues = []
    for city, neighbors in graph.items():
        for neighbor, dist in neighbors.items():
            reverse = graph.get(neighbor, {}).get(city)
            if reverse is None:
                issues.append(f"Aresta em falta no sentido inverso: {city} -> {neighbor}")
            elif reverse != dist:
                issues.append(
                    f"Distancia inconsistente entre {city} <-> {neighbor}: {dist} vs {reverse}"
                )
            if dist <= 0:
                issues.append(f"Distancia nao positiva em {city} -> {neighbor}: {dist}")
    return issues


def check_heuristic_admissible(goal: str = "Faro") -> list[str]:
    issues = []
    heuristic = get_heuristic(goal)

    for city in CITIES:
        _, optimal_cost, _ = uniform_cost_search(GRAPH, city, goal)
        h = heuristic(city)
        if h > optimal_cost:
            issues.append(
                f"Heuristica nao admissivel em {city}: h={h} > custo_otimo={optimal_cost}"
            )
    return issues


def check_heuristic_consistent(goal: str = "Faro") -> list[str]:
    issues = []
    heuristic = get_heuristic(goal)

    for city, neighbors in GRAPH.items():
        for neighbor, dist in neighbors.items():
            lhs = heuristic(city)
            rhs = dist + heuristic(neighbor)
            if lhs > rhs:
                issues.append(
                    f"Heuristica inconsistente em {city}->{neighbor}: h({city})={lhs} > {dist}+h({neighbor})={rhs}"
                )
    return issues


def compare_algorithms(goal: str = "Faro") -> dict:
    report = {
        "total_cases": 0,
        "astar_matches_ucs": 0,
        "greedy_matches_ucs": 0,
        "mismatches": [],
    }

    heuristic = get_heuristic(goal)

    for city in CITIES:
        if city == goal:
            continue

        report["total_cases"] += 1

        u_path, u_cost, _ = uniform_cost_search(GRAPH, city, goal)
        a_path, a_cost, _ = a_star_search(GRAPH, city, goal, heuristic)
        g_path, g_cost, _ = greedy_search(GRAPH, city, goal, heuristic)

        if a_cost == u_cost:
            report["astar_matches_ucs"] += 1
        else:
            report["mismatches"].append(
                f"A* != UCS para {city}->{goal}: A*={a_cost}, UCS={u_cost}"
            )

        if g_cost == u_cost:
            report["greedy_matches_ucs"] += 1

        # Verificacao adicional de integridade dos caminhos devolvidos.
        if u_path and path_cost(GRAPH, u_path) != u_cost:
            report["mismatches"].append(f"UCS caminho invalido em {city}->{goal}")
        if a_path and path_cost(GRAPH, a_path) != a_cost:
            report["mismatches"].append(f"A* caminho invalido em {city}->{goal}")
        if g_path and path_cost(GRAPH, g_path) != g_cost:
            report["mismatches"].append(f"Greedy caminho invalido em {city}->{goal}")

    return report


def main():
    print("=== SELF CHECK: IA Final Project ===")

    graph_issues = validate_graph_symmetry(GRAPH)
    adm_issues = check_heuristic_admissible("Faro")
    con_issues = check_heuristic_consistent("Faro")
    algo_report = compare_algorithms("Faro")

    print(f"\n[1] Grafo - problemas: {len(graph_issues)}")
    for issue in graph_issues[:10]:
        print(" -", issue)

    print(f"\n[2] Heuristica admissivel - problemas: {len(adm_issues)}")
    for issue in adm_issues[:10]:
        print(" -", issue)

    print(f"\n[3] Heuristica consistente - problemas: {len(con_issues)}")
    for issue in con_issues[:10]:
        print(" -", issue)

    print("\n[4] Comparacao de algoritmos (origem -> Faro)")
    print(f" - Casos avaliados: {algo_report['total_cases']}")
    print(f" - A* igual ao UCS: {algo_report['astar_matches_ucs']}")
    print(f" - Greedy igual ao UCS: {algo_report['greedy_matches_ucs']}")
    print(f" - Inconsistencias: {len(algo_report['mismatches'])}")
    for issue in algo_report["mismatches"][:10]:
        print(" -", issue)

    has_errors = bool(graph_issues or adm_issues or con_issues or algo_report["mismatches"])
    print("\nResultado final:", "COM PROBLEMAS" if has_errors else "OK")


if __name__ == "__main__":
    main()
