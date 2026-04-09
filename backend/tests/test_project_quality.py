import unittest
import sys
import importlib
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = BACKEND_ROOT / 'src'
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from app.services import normalize_plate

graph = importlib.import_module('graph')
search = importlib.import_module('search')

CITIES = graph.CITIES
GRAPH = graph.GRAPH
get_heuristic = graph.get_heuristic
a_star_search = search.a_star_search
greedy_search = search.greedy_search
uniform_cost_search = search.uniform_cost_search


class TestSearchAlgorithms(unittest.TestCase):
    def test_astar_matches_ucs_on_sample_pairs(self):
        pairs = [
            ('Braga', 'Faro'),
            ('Porto', 'Évora'),
            ('Lisboa', 'Bragança'),
            ('Aveiro', 'Beja'),
        ]

        for start, goal in pairs:
            heuristic = get_heuristic(goal)
            _, ucs_cost, _ = uniform_cost_search(GRAPH, start, goal)
            _, astar_cost, _ = a_star_search(GRAPH, start, goal, heuristic)
            self.assertAlmostEqual(ucs_cost, astar_cost, places=6)

    def test_greedy_returns_valid_path_when_reachable(self):
        start, goal = 'Porto', 'Faro'
        heuristic = get_heuristic(goal)
        greedy_path, greedy_cost, _ = greedy_search(GRAPH, start, goal, heuristic)
        _, ucs_cost, _ = uniform_cost_search(GRAPH, start, goal)

        self.assertIsNotNone(greedy_path)
        self.assertGreaterEqual(greedy_cost, ucs_cost)

    def test_general_heuristic_non_negative(self):
        goal = 'Lisboa'
        heuristic = get_heuristic(goal)
        for city in CITIES:
            self.assertGreaterEqual(heuristic(city), 0)


class TestPlateValidation(unittest.TestCase):
    def test_valid_plate_formats(self):
        valid = [
            'AA-00-BB',
            '00-AA-00',
            '00-00-AA',
            'aa00bb',
            '12ab34',
        ]
        for plate in valid:
            normalized = normalize_plate(plate)
            self.assertEqual(len(normalized), 8)
            self.assertEqual(normalized[2], '-')
            self.assertEqual(normalized[5], '-')

    def test_invalid_plate_formats(self):
        invalid = ['A-00-BB', 'AAA-00-BB', '123-AB-45', 'AA-000-BB', 'AB-CD-EF']
        for plate in invalid:
            with self.assertRaises(ValueError):
                normalize_plate(plate)


if __name__ == '__main__':
    unittest.main()
