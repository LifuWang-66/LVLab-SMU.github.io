import tempfile
import unittest
from pathlib import Path

import app as relay


class RelayServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        relay.DB_PATH = Path(self.tmpdir.name) / 'relay_state.db'
        relay._ensure_state_db()

    def tearDown(self):
        self.tmpdir.cleanup()

    def test_run_once_sends_and_dedupes(self):
        calls = []

        def fake_fetch():
            return [
                {
                    'host_name': 'PZU-104-165',
                    'host_address': '10.193.104.165',
                    'username': 'alice',
                    'email': 'alice@example.com',
                    'cc_email': 'lifu@example.com',
                    'event_type': 'gpu_count_over_8',
                    'reason': 'using 9 gpus',
                }
            ]

        def fake_send(to_email, subject, body, cc_email=None):
            calls.append((to_email, subject, body, cc_email))

        original_fetch = relay._fetch_candidates
        original_send = relay._send_email
        try:
            relay._fetch_candidates = fake_fetch
            relay._send_email = fake_send

            first = relay.run_once()
            second = relay.run_once()
        finally:
            relay._fetch_candidates = original_fetch
            relay._send_email = original_send

        self.assertEqual(first['sent'], 1)
        self.assertEqual(first['skipped'], 0)
        self.assertEqual(second['sent'], 0)
        self.assertEqual(second['skipped'], 1)
        self.assertEqual(len(calls), 1)


if __name__ == '__main__':
    unittest.main()
