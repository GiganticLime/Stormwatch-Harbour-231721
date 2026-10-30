# Stormwatch Harbour — CGD-460 Assignment 2

A Python-based multi-agent harbour simulation demonstrating intelligent agent behaviour, decision-making, and safety mechanisms.

## Features
- 24×16 grid with 4 berths and 10 dockworkers
- Ship arrivals and cargo transportation
- Storm detection and warning system
- Baseline and model-based agent policies
- Harbour Master with offline decision logic and action validation
- Performance evaluation and safety testing

## Requirements
Python 3.9+ (no additional packages required).

## How to Run

```bash
python run.py --seed 11
python run.py --all
python run.py --safety
```

## Evaluation
The simulation compares agent performance using seeds 11, 12, and 13.

Metrics include cargo delivered, storm knock-outs, invalid actions, and fallback uses.

Results are saved to `results/results.csv`.

## Conclusion
The project demonstrates multi-agent coordination, adaptive decision-making, and safety validation in a dynamic harbour environment.
