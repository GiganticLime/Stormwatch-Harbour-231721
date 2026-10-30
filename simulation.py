import random
from dataclasses import dataclass

WIDTH, HEIGHT, TICKS = 24, 16, 600
BERTHS = [(3, 0), (9, 0), (15, 0), (21, 0)]
WAREHOUSE = (0, 15)

@dataclass
class Ship:
    id: int
    berth: int
    cargo: int = 8

class Harbour:
    def __init__(self, seed, policy='baseline', master=False):
        self.rng = random.Random(seed)
        self.seed, self.policy, self.master = seed, policy, master
        self.ships = []
        self.waiting = []
        self.workers = [{'pos': WAREHOUSE, 'cargo': False, 'target': None, 'warning': False, 'ko': 0} for _ in range(10)]
        self.delivered = self.knockouts = self.invalid = self.fallbacks = 0
        self.next_ship = self.rng.randint(6, 10)
        self.next_id = 1
        # Nonoverlapping, seeded storm schedule; storm warning is five ticks ahead.
        self.storms = sorted(self.rng.sample(range(45, 550, 35), 3))
        self.held = set()

    def active(self, tick):
        return any(s <= tick < s + 15 for s in self.storms)

    def warning(self, tick):
        return any(s - 5 <= tick < s for s in self.storms)

    def report(self, tick):
        berths = ', '.join(f'B{i+1}: {next(("ship " + str(s.id) for s in self.ships if s.berth == i), "free")}' for i in range(4))
        return f'Tick {tick}; storm warning: {self.warning(tick)}; storm active: {self.active(tick)}; {berths}; waiting ships: {[s.id for s in self.waiting]}'

    def validate_action(self, action):
        if not isinstance(action, dict) or set(action) != {'action', 'ship_id'}:
            return None
        if action['action'] == 'warn_storm' and action['ship_id'] is None:
            return action
        if action['action'] == 'hold_ship' and type(action['ship_id']) is int and any(s.id == action['ship_id'] for s in self.waiting):
            return action
        return None

    def suggested_action(self, tick):
        # Offline deterministic stand-in, NOT a real LLM call. Replace this method with an API response.
        if tick % 37 == 0:
            return {'action': 'close_harbour', 'ship_id': None}
        if self.warning(tick):
            return {'action': 'warn_storm', 'ship_id': None}
        if self.waiting:
            return {'action': 'hold_ship', 'ship_id': self.waiting[0].id}
        return {'action': 'warn_storm', 'ship_id': None}

    def run(self):
        for tick in range(TICKS):
            storm, warning = self.active(tick), self.warning(tick)
            if tick == self.next_ship:
                self.waiting.append(Ship(self.next_id, -1))
                self.next_id += 1
                self.next_ship += self.rng.randint(6, 10)
            if self.master:
                action = self.validate_action(self.suggested_action(tick))
                if action is None:
                    self.invalid += 1
                    self.fallbacks += 1
                elif action['action'] == 'hold_ship':
                    self.held.add(action['ship_id'])
            for berth in range(4):
                if not any(s.berth == berth for s in self.ships) and self.waiting:
                    if storm and berth in (0, 3):
                        continue
                    available = next((s for s in self.waiting if s.id not in self.held), None)
                    if available:
                        self.waiting.remove(available)
                        available.berth = berth
                        self.ships.append(available)
            self.held.clear()
            for w in self.workers:
                if w['ko']:
                    w['ko'] -= 1
                    continue
                if self.policy == 'model' or self.master:
                    w['warning'] = warning or storm
                else:
                    w['warning'] = False
                if w['cargo']:
                    destination = WAREHOUSE
                else:
                    choices = [s for s in self.ships if s.cargo > 0 and not ((self.policy == 'model' or self.master) and w['warning'] and s.berth in (0, 3))]
                    if not choices:
                        continue
                    ship = min(choices, key=lambda s: (abs(w['pos'][0] - BERTHS[s.berth][0]) + abs(w['pos'][1] - BERTHS[s.berth][1]), s.id))
                    destination = BERTHS[ship.berth]
                if storm and w['pos'] in (BERTHS[0], BERTHS[3]):
                    self.knockouts += 1
                    w['ko'] = 10
                    w['cargo'] = False
                    w['pos'] = WAREHOUSE
                    continue
                if w['pos'] == destination:
                    if w['cargo']:
                        w['cargo'] = False
                        self.delivered += 1
                    else:
                        ship.cargo -= 1
                        w['cargo'] = True
                    continue
                x, y = w['pos']
                dx, dy = destination
                if x != dx:
                    x += 1 if dx > x else -1
                else:
                    y += 1 if dy > y else -1
                w['pos'] = (x, y)
            self.ships = [s for s in self.ships if s.cargo > 0]
        return {'seed': self.seed, 'policy': 'harbour_master_stub' if self.master else self.policy, 'cargo_delivered': self.delivered, 'storm_knockouts': self.knockouts, 'invalid_outputs': self.invalid, 'fallback_uses': self.fallbacks}
