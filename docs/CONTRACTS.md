# Contract pack v1

Only NO_ATTEMPTS and STARTED may enter dispatch. DISPATCHED and OUTCOME_UNKNOWN block replay. ACKNOWLEDGED means adapter returned, not task success. Intent identity is the canonical task digest; this intentionally deduplicates identical tasks for the life of the database.

## Interfaces and failure behavior

Read the public functions in `app.py` together with the tests. Invalid admission/task input raises `ValueError`; gateway denial raises `Denied`, runtime replay raises `Blocked`. The eval demo exits 1 if any labelled fixture fails. The other demos demonstrate expected refusals and exit 0 when the walkthrough completes.

## Trust boundary

The host process, code and local data are trusted. Source binding, durable state, and admission are distinct from identity authentication and world verification. No successful return establishes production authority.

## Schema evolution

This v1 lab has no automatic migration. Change the contracts and their rejection tests together; use a new fixture database for incompatible runtime changes.

## Runtime API

`Runtime(path)` opens a SQLite database and creates the v1 table when absent. `dispatch(task, adapter, crash=None)` accepts exactly `{"text": <string>}`. The adapter receives that task and must return JSON-serializable finite values. The result has `intent_id`, `state`, `result`, and `world_verified: false`.

`crash` is a demo fault-injection selector: `before_dispatch`, `after_dispatch`, or `after_effect`. These are test interruptions, not actual operating-system kills. `state(intent_id)` returns the stored state or `NO_ATTEMPTS`. `close()` releases the connection.

SQLite `BEGIN IMMEDIATE` records STARTED. An autocommitted conditional UPDATE reserves DISPATCHED before the adapter runs. The second connection may observe STARTED but only one conditional UPDATE succeeds. The concurrency test uses two connections in two threads; distributed and arbitrary filesystem behavior is unmeasured.

Task identity does not bind adapter code or authenticated caller identity. Use a separate database per fixture configuration; changing adapters on an existing database is unsupported. Mutable/adversarial caller objects and BaseException interruption are outside the trusted-input contract; a durable DISPATCHED marker still conservatively blocks replay on restart.
