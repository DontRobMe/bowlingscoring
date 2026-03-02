# 🎳 Bowling Scoring

Moteur de scoring bowling en Python, avec validation des entrées, système de règles pluggables et tableau de bord ASCII.

---

## Structure du projet

```
bowlingscoring/
├── bowling/
│   ├── __init__.py        # API publique
│   ├── rules.py           # Rule = Callable + RuleSet + règles prédéfinies
│   ├── scoring.py         # Logique de calcul + validation
│   └── scoreboard.py      # Tableau de bord textuel ASCII
├── tests/
│   ├── test_unit.py       # Tests unitaires (calculate_bowling_score)
│   └── test_integration.py# Tests d'intégration (get_scoreboard)
└── pyproject.toml
```

---

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate       # Windows

pip install -e ".[dev]"
```

---

## Utilisation

### `calculate_bowling_score(rolls, rules=StandardRules)`

```python
from bowling import calculate_bowling_score

print(calculate_bowling_score([10] * 12))                    # 300 — partie parfaite
print(calculate_bowling_score([0] * 20))                     # 0   — gutter game
print(calculate_bowling_score([5, 5] * 10 + [5]))            # 150 — all-spare
print(calculate_bowling_score([10, 9, 1, 5, 5, 7, 2,
                                10, 10, 10, 9, 0, 8, 2,
                                9, 1, 10]))                  # 187 — partie mixte
```

### `get_scoreboard(rolls, rules=StandardRules)`

```python
from bowling import get_scoreboard

print(get_scoreboard([10] * 12))
```

```
┌───────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┬───────┬─────────┐
│   1   │   2   │   3   │   4   │   5   │   6   │   7   │   8   │   9   │   10    │
├───────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┼─────────┤
│    X  │    X  │    X  │    X  │    X  │    X  │    X  │    X  │    X  │  X X X  │
├───────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┼───────┼─────────┤
│   30  │   60  │   90  │  120  │  150  │  180  │  210  │  240  │  270  │   300   │
└───────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┴───────┴─────────┘
```

---

## Règles de scoring

| Situation     | Calcul                                              |
|---------------|-----------------------------------------------------|
| **Strike**    | 10 + les 2 prochains lancers                        |
| **Spare**     | 10 + le prochain lancer                             |
| **Open**      | Somme des 2 lancers du frame                        |
| **10e frame** | Strike ou spare → lancers bonus supplémentaires     |

---

## Système de règles pluggables

Les règles sont des **fonctions** (`Rule = Callable`) passées à un `RuleSet`.

### Règles disponibles

| Fonction                 | Rôle                                      |
|--------------------------|-------------------------------------------|
| `strike_bonus_rule`      | Strike = 10 + 2 prochains lancers         |
| `strike_no_bonus_rule`   | Strike = 10 (sans bonus)                  |
| `spare_bonus_rule`       | Spare = 10 + prochain lancer              |
| `spare_double_bonus_rule`| Spare = 10 + prochain lancer × 2          |
| `spare_no_bonus_rule`    | Spare = 10 (sans bonus)                   |
| `open_frame_rule`        | Open = somme des 2 lancers                |

### Variantes prédéfinies

| RuleSet           | Frames | Quilles | Strike        | Spare          |
|-------------------|--------|---------|---------------|----------------|
| `StandardRules`   | 10     | 10      | bonus         | bonus          |
| `NinePinRules`    | 9      | 9       | bonus         | bonus          |
| `FiveFrameRules`  | 5      | 10      | bonus         | bonus          |
| `NoBonus`         | 10     | 10      | sans bonus    | sans bonus     |
| `DoubleSpareRules`| 10     | 10      | bonus         | bonus × 2      |

### Utiliser une variante

```python
from bowling import calculate_bowling_score, get_scoreboard, FiveFrameRules, NoBonus

print(calculate_bowling_score([10] * 7, rules=FiveFrameRules))   # 150
print(calculate_bowling_score([10] * 12, rules=NoBonus))         # 100
print(get_scoreboard([10] * 7, rules=FiveFrameRules))
```

### Créer sa propre règle

```python
from bowling import RuleSet, calculate_bowling_score
from bowling.rules import spare_bonus_rule, open_frame_rule

# Strike toujours = 30, spare et open normaux
MyRules = RuleSet(
    name="TripleStrike",
    max_pins=10,
    max_frames=10,
    strike_rule=lambda rolls, frame, i: (30, 1),
    spare_rule=spare_bonus_rule,
    open_rule=open_frame_rule,
    tenth_frame_extra=False,
)

print(calculate_bowling_score([10] + [0] * 18, rules=MyRules))   # 30
```

---

## Lancer les tests

```bash
pytest                                     # tous les tests
pytest tests/test_unit.py -v              # tests unitaires uniquement
pytest tests/test_integration.py -v       # tests d'intégration uniquement
```

### Répartition

| Fichier                | Type          | Tests |
|------------------------|---------------|-------|
| `test_unit.py`         | Unitaires     | 93    |
| `test_integration.py`  | Intégration   | 47    |
| **Total**              |               | **120** |

---

## Validation

`BowlingError` (sous-classe de `ValueError`) est levée si :

- Un lancer est hors de la plage `[0, max_pins]`
- La somme de deux lancers d'un frame dépasse `max_pins`
- La séquence est trop courte ou mal formée
- Les lancers bonus du dernier frame sont manquants ou invalides
