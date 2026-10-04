# Agent Runtime Recovery Lab

A small, runnable runtime/evidence fixture for **Agentic Systems / AI Infrastructure** review. Standard-library Python 3.11+; no API key, installation, or external service required.

## Run in under a minute

```sh
git clone https://github.com/afimeth/agent-runtime-recovery-lab.git
cd agent-runtime-recovery-lab
python -m unittest discover -s tests -v
python app.py
```

The demo uses synthetic inputs and prints JSON. Tests fail with a nonzero exit code. The runtime demo creates and removes a temporary SQLite database; other demos operate in memory.

## Headless click-to-run contract

`python app.py` is the runtime entrypoint. Treat it as the headless equivalent of a click-to-run action: one invocation enters the fixture, executes the defined flow, and returns machine-readable output.

No UI is required or shipped. A CLI, IDE action, web surface, desktop shell, or other interface may wrap the same runtime without changing its evidence semantics.

## What this demonstrates

Implemented a SQLite-backed agent execution fixture with durable dispatch markers, conservative crash recovery, and replay suppression tests.

Flow: `NO_ATTEMPTS -> STARTED -> DISPATCHED -> ACKNOWLEDGED | OUTCOME_UNKNOWN`.

See [architecture](docs/ARCHITECTURE.md), [contracts](docs/CONTRACTS.md), [evidence and limitations](docs/EVIDENCE.md), and [demo walkthrough](docs/DEMO.md).

## Boundaries

No live model, network adapter, distributed coordination, authenticated owner, hostile database protection, human resolution, cancellation, scheduling, or exactly-once guarantee. Process crashes are injected exceptions; real SIGKILL and power-loss durability are unmeasured. SQLite commit precedes adapter entry, leaving a conservative uncertainty window.

This is a fixture implementation, not a production service or an accepted release of its source project. CI results and local measurements are separate evidence.

## Provenance

The implementation is a fresh, standalone educational distillation of inspected private runtime contracts. No private source files, customer data, credentials, topology, or private project identifiers are included. The private source manifest is retained outside this public repository. No license is assigned to the original private sources; this repository grants no rights to them.

## Extension boundary

Describe the failure boundary, run the denial/adversarial tests, and state what new evidence would be needed before production use. Start with a durable audit/identity boundary, then add provider integration and measured operational behavior.
