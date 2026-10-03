# Demo walkthrough

1. Run `python -m unittest discover -s tests -v`.
2. Run `python app.py` and inspect the JSON.
3. Read each test containing `failure`, `replay`, `restart`, `fabricated`, `modified`, or `concurrent` to locate the negative proof.
4. Explain the conservative boundary and its limits in `CONTRACTS.md` and `EVIDENCE.md`.

Role scenario: **Agentic Systems / AI Infrastructure**.

Safe CV wording: "Implemented a SQLite-backed agent execution fixture with durable dispatch markers, conservative crash recovery, and replay suppression tests."

Do not claim production deployment, real provider integration, generalized agent reliability, source truth, or MCP compatibility from this demo.
