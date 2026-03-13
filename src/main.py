# main.py
# Programa principal - Trabalho Prático Final IA 2026

import os
import sys

# Garante que os módulos locais são encontrados quando executado a partir
# de qualquer diretório
sys.path.insert(0, os.path.dirname(__file__))

from graph  import GRAPH, CITIES, get_heuristic
from search import (
    uniform_cost_search,
    depth_limited_search,
    greedy_search,
    a_star_search,
)
from ocr import read_plate_from_image
from llm import get_city_attractions, list_available_models, DEFAULT_MODEL

# ─────────────────────────────────────────────────────────────────────────────
# Constantes de formatação
# ─────────────────────────────────────────────────────────────────────────────
LINE  = "─" * 62
DLINE = "═" * 62


# ─────────────────────────────────────────────────────────────────────────────
# Utilitários de apresentação
# ─────────────────────────────────────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def header(title: str):
    print(f"\n{DLINE}")
    print(f"  {title}")
    print(DLINE)


def pause():
    input("\n  Pressiona Enter para continuar...")


def print_iterations(iterations: list, algorithm: str):
    """Imprime a tabela de iterações de acordo com o algoritmo."""
    header(f"Iterações — {algorithm}")

    if algorithm == "Custo Uniforme":
        print(f"  {'#':>4}  {'Nó':<22}  {'g(n)':>7}  Caminho")
        print(f"  {LINE}")
        for i, it in enumerate(iterations, 1):
            path_str = " → ".join(it['path'])
            print(f"  {i:>4}  {it['node']:<22}  {it['g']:>6} km  {path_str}")

    elif algorithm == "Profundidade Limitada":
        print(f"  {'#':>4}  {'Nó':<22}  {'Prof.':>6}  {'g(n)':>7}  Caminho")
        print(f"  {LINE}")
        for i, it in enumerate(iterations, 1):
            path_str = " → ".join(it['path'])
            print(f"  {i:>4}  {it['node']:<22}  {it['depth']:>6}  {it['g']:>6} km  {path_str}")

    elif algorithm == "Sôfrega":
        print(f"  {'#':>4}  {'Nó':<22}  {'h(n)':>7}  {'g(n)':>7}  Caminho")
        print(f"  {LINE}")
        for i, it in enumerate(iterations, 1):
            path_str = " → ".join(it['path'])
            print(f"  {i:>4}  {it['node']:<22}  {it['h']:>6} km  {it['g']:>6} km  {path_str}")

    elif algorithm == "A*":
        print(f"  {'#':>4}  {'Nó':<22}  {'f(n)':>7}  {'g(n)':>7}  {'h(n)':>7}  Caminho")
        print(f"  {LINE}")
        for i, it in enumerate(iterations, 1):
            path_str = " → ".join(it['path'])
            print(f"  {i:>4}  {it['node']:<22}  {it['f']:>6} km  {it['g']:>6} km  {it['h']:>6} km  {path_str}")


def print_result(path, cost, algorithm: str):
    """Imprime o caminho final e distância."""
    header(f"Resultado — {algorithm}")
    if path:
        print(f"  Caminho  : {' → '.join(path)}")
        print(f"  Distância: {cost} km")
    else:
        print("  Nenhum caminho encontrado com os parâmetros dados.")
    print(DLINE)


# ─────────────────────────────────────────────────────────────────────────────
# Login via OCR
# ─────────────────────────────────────────────────────────────────────────────

def login() -> str:
    """Fluxo de autenticação por matrícula (OCR ou manual)."""
    clear()
    header("LOGIN — Reconhecimento de Matrícula (OCR)")
    print("""
  Para entrar no programa é necessário identificar o veículo
  através da sua matrícula.

  Opções:
    1. Fornecer imagem da matrícula (OCR automático)
    2. Introduzir matrícula manualmente
""")

    while True:
        choice = input("  Escolha [1/2]: ").strip()

        if choice == "1":
            path = input("  Caminho para a imagem: ").strip().strip('"')
            try:
                print("  A processar imagem com OCR...")
                plate = read_plate_from_image(path)
                if plate:
                    print(f"\n  Matrícula reconhecida: {plate}")
                    confirm = input("  Confirmar? (s/n): ").strip().lower()
                    if confirm == "s":
                        return plate
                    else:
                        print("  Tenta novamente.")
                else:
                    print("  Não foi possível reconhecer uma matrícula na imagem.")
            except FileNotFoundError as e:
                print(f"  Erro: {e}")
            except ImportError as e:
                print(f"  Erro: {e}")

        elif choice == "2":
            plate = input("  Matrícula (ex: AA-00-BB): ").strip().upper()
            if plate:
                return plate
            else:
                print("  Matrícula não pode estar vazia.")
        else:
            print("  Opção inválida.")


# ─────────────────────────────────────────────────────────────────────────────
# Seleção de cidades
# ─────────────────────────────────────────────────────────────────────────────

def choose_city(prompt: str, exclude: str = None) -> str:
    """Apresenta a lista de cidades e pede ao utilizador para escolher uma."""
    cities = [c for c in CITIES if c != exclude]
    print(f"\n  {prompt}")
    for i, city in enumerate(cities, 1):
        print(f"    {i:>2}. {city}")

    while True:
        choice = input("\n  Número da cidade: ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(cities):
                return cities[idx]
        print("  Opção inválida. Tenta novamente.")


# ─────────────────────────────────────────────────────────────────────────────
# Menu de algoritmos
# ─────────────────────────────────────────────────────────────────────────────

def choose_algorithm() -> str:
    header("Selecionar Algoritmo de Procura")
    print("""
  Procura Cega:
    1. Custo Uniforme
    2. Profundidade Limitada

  Procura Heurística (heurística otimizada para destino = Faro):
    3. Sôfrega (Greedy Best-First)
    4. A*

    5. Executar todos os algoritmos
""")
    options = {"1", "2", "3", "4", "5"}
    while True:
        choice = input("  Escolha [1-5]: ").strip()
        if choice in options:
            return choice
        print("  Opção inválida.")


# ─────────────────────────────────────────────────────────────────────────────
# Execução de um algoritmo
# ─────────────────────────────────────────────────────────────────────────────

def run_algorithm(name: str, start: str, goal: str, limit: int = None):
    """Executa um algoritmo, imprime iterações e resultado."""
    heuristic = get_heuristic(goal)
    path = cost = iterations = None

    if name == "Custo Uniforme":
        path, cost, iterations = uniform_cost_search(GRAPH, start, goal)

    elif name == "Profundidade Limitada":
        path, cost, iterations = depth_limited_search(GRAPH, start, goal, limit)

    elif name == "Sôfrega":
        path, cost, iterations = greedy_search(GRAPH, start, goal, heuristic)

    elif name == "A*":
        path, cost, iterations = a_star_search(GRAPH, start, goal, heuristic)

    print_iterations(iterations, name)
    print_result(path, cost, name)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# LLM — atrações turísticas
# ─────────────────────────────────────────────────────────────────────────────

def show_attractions(path: list, model: str):
    """Para cada cidade no caminho, consulta o LLM para as 3 principais atrações."""
    if not path:
        return

    header("Atrações Turísticas — LLM Local")
    print(f"  Modelo: {model}\n")

    for city in path:
        print(f"  {'─'*58}")
        print(f"  📍 {city}")
        print(f"  {'─'*58}")
        print("  A consultar LLM...")
        result = get_city_attractions(city, model)
        # Indentar cada linha da resposta
        for line in result.splitlines():
            print(f"    {line}")
        print()

    pause()


# ─────────────────────────────────────────────────────────────────────────────
# Programa principal
# ─────────────────────────────────────────────────────────────────────────────

def main():
    # 1. Login
    plate = login()

    # 2. Ecrã principal
    clear()
    header(f"Bem-vindo! Veículo identificado: {plate}")
    print("""
  Este programa encontra o caminho mais eficiente entre duas
  cidades Portuguesas usando diferentes algoritmos de procura.
""")
    pause()

    # 3. Escolha do modelo LLM
    clear()
    header("Configuração do LLM Local (Ollama)")
    available = list_available_models()
    if available:
        print(f"  Modelos disponíveis: {', '.join(available)}")
    else:
        print("  (Ollama não disponível ou sem modelos instalados)")
    model_input = input(f"\n  Modelo a usar [{DEFAULT_MODEL}]: ").strip()
    llm_model = model_input if model_input else DEFAULT_MODEL

    while True:
        # 4. Escolha de cidades
        clear()
        header("Configuração da Rota")
        start = choose_city("Cidade de ORIGEM:")
        goal  = choose_city("Cidade de DESTINO:", exclude=start)

        if goal != "Faro":
            print("\n  ⚠  Nota: a heurística fornecida é optimizada para destino = Faro.")
            print("     Para outros destinos, os algoritmos A* e Sôfrega comportam-se")
            print("     de forma não-informada (h=0).")

        # 5. Escolha de algoritmo
        algo_choice = choose_algorithm()

        # Limite de profundidade (DLS)
        depth_limit = None
        if algo_choice in ("2", "5"):
            while True:
                val = input("\n  Limite de profundidade (DLS): ").strip()
                if val.isdigit() and int(val) > 0:
                    depth_limit = int(val)
                    break
                print("  Valor inválido. Introduz um inteiro positivo.")

        clear()
        algos_map = {
            "1": ["Custo Uniforme"],
            "2": ["Profundidade Limitada"],
            "3": ["Sôfrega"],
            "4": ["A*"],
            "5": ["Custo Uniforme", "Profundidade Limitada", "Sôfrega", "A*"],
        }
        algos = algos_map[algo_choice]

        final_paths = {}
        for algo in algos:
            lim = depth_limit if algo == "Profundidade Limitada" else None
            result_path = run_algorithm(algo, start, goal, lim)
            final_paths[algo] = result_path
            pause()

        # 6. Atrações turísticas via LLM
        # Usa o caminho do último algoritmo executado (ou o mais adequado)
        best_path = None
        for algo in ["A*", "Custo Uniforme", "Sôfrega", "Profundidade Limitada"]:
            if algo in final_paths and final_paths[algo]:
                best_path = final_paths[algo]
                break

        show_llm = input("\n  Mostrar atrações turísticas das cidades do caminho? (s/n): ").strip().lower()
        if show_llm == "s":
            show_attractions(best_path, llm_model)

        # 7. Repetir?
        again = input("  Nova pesquisa? (s/n): ").strip().lower()
        if again != "s":
            break

    print(f"\n  Até logo! Veículo {plate} — boa viagem!\n")


if __name__ == "__main__":
    main()
