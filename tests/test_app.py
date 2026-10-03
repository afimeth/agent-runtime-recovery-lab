import hashlib, json, sqlite3, tempfile, unittest
from pathlib import Path
from app import Runtime, Blocked, fixture

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / 'state.sqlite'
        self.r = Runtime(self.path)
        self.task = {'text': 'hello'}
        self.calls = 0
    def tearDown(self):
        self.r.close()
        self.tmp.cleanup()
    def adapter(self, task):
        self.calls += 1
        return fixture(task)
    def test_success_and_duplicate(self):
        out = self.r.dispatch(self.task, self.adapter)
        self.assertEqual(out['result'], {'uppercase': 'HELLO'})
        self.assertFalse(out['world_verified'])
        with self.assertRaises(Blocked): self.r.dispatch(self.task, self.adapter)
        self.assertEqual(self.calls, 1)
    def test_restart_uncertainty(self):
        with self.assertRaises(RuntimeError): self.r.dispatch(self.task, self.adapter, 'after_dispatch')
        self.r.close()
        self.r = Runtime(self.path)
        with self.assertRaisesRegex(Blocked, 'DISPATCHED'): self.r.dispatch(self.task, self.adapter)
        self.assertEqual(self.calls, 0)
    def test_pre_dispatch_retry(self):
        with self.assertRaises(RuntimeError): self.r.dispatch(self.task, self.adapter, 'before_dispatch')
        self.r.dispatch(self.task, self.adapter)
        self.assertEqual(self.calls, 1)
    def test_effect_then_failure_holds(self):
        with self.assertRaises(RuntimeError): self.r.dispatch(self.task, self.adapter, 'after_effect')
        with self.assertRaisesRegex(Blocked, 'OUTCOME_UNKNOWN'): self.r.dispatch(self.task, self.adapter)
        self.assertEqual(self.calls, 1)
    def test_bad_result_holds(self):
        with self.assertRaises(ValueError): self.r.dispatch(self.task, lambda _: float('nan'))
        with self.assertRaises(Blocked): self.r.dispatch(self.task, self.adapter)
        self.assertEqual(self.calls, 0)
    def test_invalid_task_never_called(self):
        for task in (None, {}, {'text': 1}, {'text': 'x', 'extra': 1}):
            with self.assertRaises(ValueError): self.r.dispatch(task, self.adapter)
        self.assertEqual(self.calls, 0)
    def test_independent_intents(self):
        self.r.dispatch(self.task, self.adapter)
        self.r.dispatch({'text': 'other'}, self.adapter)
        self.assertEqual(self.calls, 2)
    def test_second_connection_cannot_replay(self):
        second = Runtime(self.path)
        try:
            self.r.dispatch(self.task, self.adapter)
            with self.assertRaises(Blocked): second.dispatch(self.task, self.adapter)
        finally: second.close()
        self.assertEqual(self.calls, 1)
    def test_dispatch_marker_visible_before_adapter(self):
        def observe(task):
            db = sqlite3.connect(self.path)
            try: self.assertEqual(db.execute('SELECT state FROM intents').fetchone()[0], 'DISPATCHED')
            finally: db.close()
            return fixture(task)
        self.r.dispatch(self.task, observe)

    def test_concurrent_connections_enter_adapter_once(self):
        import concurrent.futures, threading
        barrier = threading.Barrier(2)
        lock = threading.Lock()
        calls = []
        def work(_):
            r = Runtime(self.path)
            def effect(task):
                with lock: calls.append(task)
                return fixture(task)
            try:
                barrier.wait(timeout=5)
                try: r.dispatch(self.task, effect); return 'ACKNOWLEDGED'
                except Blocked: return 'BLOCKED'
            finally: r.close()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            outcomes = list(pool.map(work, range(2)))
        self.assertEqual(sorted(outcomes), ['ACKNOWLEDGED', 'BLOCKED'])
        self.assertEqual(len(calls), 1)
