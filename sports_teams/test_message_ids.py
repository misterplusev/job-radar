"""Sports-teams deliveries record the Discord message ID. No network is used."""
import io
import json
import os
import unittest
from unittest.mock import patch

import cloud_storage
import publish_teams as pub


class Reply(io.BytesIO):
    def __init__(self, status, body=b''):
        super().__init__(body)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class NotifyReturnsTheMessageId(unittest.TestCase):
    def send(self, reply):
        seen = {}

        def urlopen(req, timeout=30):
            seen['url'] = req.full_url
            return reply
        with patch.object(pub, 'guard'), patch.object(pub.urllib.request, 'urlopen', urlopen):
            return pub.notify('https://discord.invalid/api/webhooks/1/token', {'content': 'x'}), seen['url']

    def test_wait_true_is_requested_and_the_id_is_returned(self):
        body = json.dumps({'id': '1570000000000000001', 'channel_id': '1569043665345708344'}).encode()
        result, url = self.send(Reply(200, body))
        self.assertEqual(result, '1570000000000000001')
        self.assertTrue(url.endswith('?wait=true'))

    def test_accepted_without_a_body_is_still_success(self):
        result, _ = self.send(Reply(204))
        self.assertIs(result, True)


class LedgerRecordsTheMessageId(unittest.TestCase):
    def storage(self):
        with patch.dict(os.environ, {'SUPABASE_URL': 'https://example.com', 'SUPABASE_SERVICE_ROLE_KEY': 'mock'}):
            return cloud_storage.CloudStorage()

    def test_ids_are_written_when_the_column_exists(self):
        s = self.storage()
        with patch.object(s, 'rows', return_value=[]), patch.object(s, 'has_message_id_column', return_value=True), \
                patch.object(s, 'upsert') as up:
            s.save_notification_state({'seen': ['a', 'b'], 'posted_at': 'now', 'message_ids': {'a': '111', 'b': '111'}})
        self.assertEqual(up.call_args.args[1], [
            {'url': 'a', 'status': 'delivered', 'delivered_at': 'now', 'discord_message_id': '111'},
            {'url': 'b', 'status': 'delivered', 'delivered_at': 'now', 'discord_message_id': '111'}])

    def test_rows_are_unchanged_while_the_column_is_absent(self):
        s = self.storage()
        with patch.object(s, 'rows', return_value=[]), patch.object(s, 'has_message_id_column', return_value=False), \
                patch.object(s, 'upsert') as up:
            s.save_notification_state({'seen': ['a'], 'posted_at': 'now', 'message_ids': {'a': '111'}})
        self.assertEqual(up.call_args.args[1], [{'url': 'a', 'status': 'delivered', 'delivered_at': 'now'}])

    def test_the_column_check_reads_one_row_and_maps_an_error_to_absent(self):
        s = self.storage()
        with patch.object(s, 'request') as request:
            self.assertTrue(s.has_message_id_column())
            self.assertEqual(request.call_args.kwargs['params'], {'select': 'discord_message_id', 'limit': 1})
            request.side_effect = RuntimeError('Supabase GET team_job_notifications HTTP 400')
            self.assertFalse(s.has_message_id_column())


class MainKeepsTheIdPerJob(unittest.TestCase):
    def test_each_job_in_a_message_records_that_message_id(self):
        rows = [{'url': f'https://example.com/{i}', 'title': f'T{i}', 'team': 'Team', 'league': 'NBA',
                 'posted_at': pub.now_iso(), 'first_seen_at': pub.now_iso()} for i in range(6)]
        state = {'seen': [], 'pending': [r['url'] for r in rows], 'posts': 0}
        saved = []
        ids = iter(['m1', 'm2'])
        with patch.object(pub, 'load_rows', return_value=rows), patch.object(pub, 'load_state', return_value=state), \
                patch.object(pub, 'save_state', side_effect=lambda s: saved.append(json.loads(json.dumps(s)))), \
                patch.object(pub, 'guard'), patch.object(pub, 'webhook', return_value='https://discord.invalid/x'), \
                patch.object(pub, 'notify', side_effect=lambda *a, **k: next(ids)), \
                patch.object(pub.time, 'sleep'), patch('sys.argv', ['publish_teams.py', '--post', '--limit', '0']):
            self.assertEqual(pub.main(), 0)
        final = saved[-1]['message_ids']
        self.assertEqual(sorted(set(final.values())), ['m1', 'm2'])
        self.assertEqual(len(final), 6)
        self.assertEqual(sum(1 for v in final.values() if v == 'm1'), 5)


if __name__ == '__main__':
    unittest.main()
