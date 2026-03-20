Repository for the Final Project of the Artificial Intelligence Curricular Unit


# Authors
David Borges

Patricia Oliveira

Susana Tavares


## How to run

1. Install dependencies:

	pip install -r requirements.txt

2. Start the app:

	python src/main.py

3. Optional validation (recommended before delivery):

	python src/self_check.py


## What the validation checks

- Graph consistency (bidirectional edges and positive distances)
- Heuristic quality for Faro (admissibility and consistency)
- Cost optimality comparison between UCS and A*
- Path integrity (path cost matches reported algorithm cost)
