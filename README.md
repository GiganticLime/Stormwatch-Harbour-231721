# Stormwatch Harbour — CGD-460 Assignment 2 starter

Requires Python 3.9+; no third-party packages for simulation.

```bash
python run.py --seed 11
python run.py --all
python run.py --safety
```

`--all` writes `results/results.csv`. The Harbour Master is an **offline mock**, not a genuine LLM integration. To meet the LLM requirement, replace `suggested_action()` with an actual model call returning a structured action, retaining `validate_action()` and fallback handling. Explain this distinction in your submission. The simulation is a starter design: review the worker movement, storm timing, ship handling, and test validity before submitting.
