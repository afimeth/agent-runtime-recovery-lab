# Evidence and limitations

Measured: 2026-10-03T15:55:26.672825+00:00. Python 3.14.7, Windows local execution.

`python -m unittest discover -s tests -v`: **10 passed**, exit 0.
`python app.py`: exit 0. See [test output](../evidence/local-tests.txt) and [demo JSON](../evidence/demo.json).

This is producer-run local validation, not an independent review. GitHub CI is a separate run; inspect Actions for its actual status. No L3/L4 acceptance, live provider evidence or production validation is claimed.

No live model, network adapter, distributed coordination, authenticated owner, hostile database protection, human resolution, cancellation, scheduling, or exactly-once guarantee. Process crashes are injected exceptions; real SIGKILL and power-loss durability are unmeasured. SQLite commit precedes adapter entry, leaving a conservative uncertainty window.

Safe CV claim: "Implemented a SQLite-backed agent execution fixture with durable dispatch markers, conservative crash recovery, and replay suppression tests."
