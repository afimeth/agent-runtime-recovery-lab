"""Single-process fixture dispatcher with durable uncertainty, not exactly-once."""
import argparse
import hashlib
import json
import sqlite3
import tempfile
from pathlib import Path

class Blocked(ValueError):
    pass

class Runtime:
    def __init__(self, path):
        self.db = sqlite3.connect(path, isolation_level=None)
        self.db.execute('PRAGMA busy_timeout=3000')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS intents(id TEXT PRIMARY KEY, payload TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN (\'STARTED\',\'DISPATCHED\',\'ACKNOWLEDGED\',\'OUTCOME_UNKNOWN\')), result TEXT)')

    def close(self):
        self.db.close()

    def state(self, intent):
        row = self.db.execute('SELECT state FROM intents WHERE id=?', (intent,)).fetchone()
        return row[0] if row else 'NO_ATTEMPTS'

    def dispatch(self, task, adapter, crash=None):
        if not isinstance(task, dict) or set(task) != {'text'} or not isinstance(task['text'], str):
            raise ValueError('TASK_INVALID')
        payload = json.dumps(task, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)
        intent = hashlib.sha256(payload.encode()).hexdigest()
        self.db.execute('BEGIN IMMEDIATE')
        try:
            state = self.state(intent)
            if state not in ('NO_ATTEMPTS', 'STARTED'):
                raise Blocked(state)
            self.db.execute('INSERT OR IGNORE INTO intents VALUES(?,?,?,NULL)', (intent, payload, 'STARTED'))
            self.db.execute('COMMIT')
        except BaseException:
            self.db.execute('ROLLBACK')
            raise
        if crash == 'before_dispatch':
            raise RuntimeError('SIMULATED_CRASH')
        # Compare-and-set prevents two contenders from entering this effect path.
        changed = self.db.execute("UPDATE intents SET state='DISPATCHED' WHERE id=? AND state='STARTED'", (intent,)).rowcount
        if changed != 1:
            raise Blocked(self.state(intent))
        if crash == 'after_dispatch':
            raise RuntimeError('SIMULATED_CRASH')
        try:
            result = adapter(task)
            encoded = json.dumps(result, sort_keys=True, allow_nan=False)
            if crash == 'after_effect':
                raise RuntimeError('SIMULATED_CRASH')
        except Exception:
            self.db.execute("UPDATE intents SET state='OUTCOME_UNKNOWN' WHERE id=?", (intent,))
            raise
        self.db.execute("UPDATE intents SET state='ACKNOWLEDGED', result=? WHERE id=?", (encoded, intent))
        return {'intent_id': intent, 'state': self.state(intent), 'result': result, 'world_verified': False}

def fixture(task):
    return {'uppercase': task['text'].upper()}

def demo():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'runtime.sqlite'
        task = {'text': 'bounded agent execution'}
        r = Runtime(path)
        good = r.dispatch(task, fixture)
        duplicate = None
        try:
            r.dispatch(task, fixture)
        except Blocked as e:
            duplicate = str(e)
        uncertain = {'text': 'interrupted effect'}
        try:
            r.dispatch(uncertain, fixture, 'after_dispatch')
        except RuntimeError:
            pass
        r.close()
        r = Runtime(path)
        try:
            r.dispatch(uncertain, fixture)
        except Blocked as e:
            recovery = str(e)
        r.close()
        return {'success': good, 'duplicate_blocked': duplicate, 'restart_blocked': recovery}

if __name__ == '__main__':
    print(json.dumps(demo(), indent=2))
