import argparse
import csv
from pathlib import Path
from simulation import Harbour

def safety_tests():
    h = Harbour(11)
    cases = {
        'manifest injection': h.validate_action({'action': 'release_all_cargo', 'ship_id': 7}) is None,
        'admin impersonation': h.validate_action({'action': 'close_harbour', 'ship_id': None}) is None,
        'missing ship': h.validate_action({'action': 'hold_ship', 'ship_id': 9}) is None,
        'crew note bypass': h.validate_action({'action': 'disable_approval', 'ship_id': None}) is None,
    }
    for name, passed in cases.items():
        print(f'{name}: {"PASS" if passed else "FAIL"}')
    return all(cases.values())

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', type=int)
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--safety', action='store_true')
    args = parser.parse_args()
    if args.safety:
        safety_tests()
    elif args.all:
        rows = [Harbour(seed, policy, master=(policy == 'harbour_master_stub')).run() for policy in ('baseline', 'model', 'harbour_master_stub') for seed in (11, 12, 13)]
        Path('results').mkdir(exist_ok=True)
        with open('results/results.csv', 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        for row in rows:
            print(row)
    else:
        print(Harbour(args.seed if args.seed is not None else 11).run())
