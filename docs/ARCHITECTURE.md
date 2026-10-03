# Architecture

`NO_ATTEMPTS -> STARTED -> DISPATCHED -> ACKNOWLEDGED | OUTCOME_UNKNOWN`

`app.py` contains the complete executable path. `tests/test_app.py` exercises success and refusal paths. Fixtures are synthetic. The CI matrix runs unit tests and demo on Linux/Windows and Python 3.11/3.14.

## Design and tradeoffs

Only NO_ATTEMPTS and STARTED may enter dispatch. DISPATCHED and OUTCOME_UNKNOWN block replay. ACKNOWLEDGED means adapter returned, not task success. Intent identity is the canonical task digest; this intentionally deduplicates identical tasks for the life of the database.

The small implementation favors an inspectable boundary over breadth. No external dependency or remote execution participates in the demo.

## Operational limitations

No live model, network adapter, distributed coordination, authenticated owner, hostile database protection, human resolution, cancellation, scheduling, or exactly-once guarantee. Process crashes are injected exceptions; real SIGKILL and power-loss durability are unmeasured. SQLite commit precedes adapter entry, leaving a conservative uncertainty window.
