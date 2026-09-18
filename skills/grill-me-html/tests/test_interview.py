import copy
import importlib.util
import json
import shlex
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'interview.py'
spec = importlib.util.spec_from_file_location('interview', SCRIPT)
interview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(interview)


def section(section_id='scope'):
    return {'id': section_id, 'title': 'Scope', 'remaining': {'min': 0, 'max': 3}, 'questions': [
        {'id': 'q1', 'title': 'Location?', 'body': 'Where should it run?', 'recommendation': 'Local browser'},
        {'id': 'q2', 'title': 'Return path?', 'body': 'How should answers return?', 'recommendation': 'Active session'},
    ]}


def answers(section_id='scope'):
    return {'section': section_id, 'answers': {
        'q1': {'mode': 'accepted', 'text': 'Forged client text'},
        'q2': {'mode': 'custom', 'text': 'Keep this session active.\nPreserve Unicode: café ✓'},
    }}


class InterviewTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        interview.write_json(self.directory / 'state.json', {
            'title': 'Interview', 'sections': [], 'remaining': None, 'finished': False,
        })
        interview.publish(self.directory, section())
        self.server = interview.make_server(self.directory, 'secret')
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.close)
        self.url = f'http://127.0.0.1:{self.server.server_port}/secret/'

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self, path, payload=None, headers=None):
        request_headers = {'Content-Type': 'application/json'}
        request_headers.update(headers or {})
        req = Request(self.url + path, data=None if payload is None else json.dumps(payload).encode(), headers=request_headers)
        with urlopen(req, timeout=3) as response:
            return json.load(response)

    def test_exact_answers_return_to_waiter_and_survive_read(self):
        result = []
        waiter = threading.Thread(target=lambda: result.append(interview.wait_for_answers(self.directory, 'scope', 3)))
        waiter.start()
        self.request('answers', answers())
        waiter.join(4)
        self.assertFalse(waiter.is_alive())
        self.assertEqual(result[0]['status'], 'answered')
        returned = result[0]['section']['answers']
        self.assertEqual(returned['q1'], {'mode': 'accepted', 'text': 'Local browser'})
        self.assertEqual(returned['q2'], answers()['answers']['q2'])
        self.assertEqual(interview.wait_for_answers(self.directory, 'scope', 1), result[0])
        self.assertEqual(interview.read_json(self.directory / 'state.json')['sections'][0]['answers'], returned)

    def test_timeout_does_not_submit(self):
        self.assertEqual(interview.wait_for_answers(self.directory, 'scope', 0), {'status': 'waiting', 'section': 'scope'})
        self.assertNotIn('answers', self.request('state')['sections'][0])

    def test_partial_empty_and_unknown_answers_fail(self):
        invalid = [None, [], {}, answers(), answers(), answers(), answers()]
        invalid[3]['answers'].pop('q2')
        invalid[4]['answers']['q2']['text'] = '  '
        invalid[5]['section'] = 'missing'
        invalid[6]['answers']['q2']['mode'] = 'guessed'
        for payload in invalid:
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                interview.submit(self.directory, payload)
        self.assertNotIn('answers', self.request('state')['sections'][0])

    def test_retry_is_idempotent_and_conflicting_submission_fails(self):
        self.request('answers', answers())
        self.request('answers', answers())
        changed = answers()
        changed['answers']['q2']['text'] = 'Different decision'
        with self.assertRaises(HTTPError) as error:
            self.request('answers', changed)
        self.assertEqual(error.exception.code, 400)
        self.assertEqual(self.request('state')['sections'][0]['answers']['q2']['text'], answers()['answers']['q2']['text'])

    def test_followup_requires_answers_and_keeps_history(self):
        with self.assertRaises(ValueError):
            interview.publish(self.directory, section('next'))
        self.request('answers', answers())
        followup = section('next')
        followup['remaining'] = {'min': 0, 'max': 0}
        interview.publish(self.directory, followup)
        state = self.request('state')
        self.assertEqual(state['remaining'], {'min': 0, 'max': 0})
        self.assertEqual(len(state['sections']), 2)
        self.assertIn('answers', state['sections'][0])
        self.assertNotIn('answers', state['sections'][1])
        with self.assertRaises(ValueError):
            interview.publish(self.directory, section())

    def test_invalid_sections_leave_state_unchanged(self):
        before = self.request('state')
        invalid = section('next')
        invalid['questions'].append(copy.deepcopy(invalid['questions'][0]))
        for payload in ([], {}, invalid, {**section('next'), 'remaining': {'min': 4, 'max': 2}},
                        {**section('next'), 'remaining': {'min': False, 'max': 2}}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                interview.publish(self.directory, payload)
        self.assertEqual(self.request('state'), before)

    def test_other_origins_hosts_and_tokens_cannot_read_or_submit(self):
        for headers in ({'Origin': 'http://evil.test'}, {'Host': 'evil.test'}):
            with self.subTest(headers=headers), self.assertRaises(HTTPError) as error:
                self.request('answers', answers(), headers)
            self.assertEqual(error.exception.code, 403)
        with self.assertRaises(HTTPError) as error:
            urlopen(self.url.replace('/secret/', '/other/') + 'state', timeout=2)
        self.assertEqual(error.exception.code, 404)
        self.assertNotIn('answers', self.request('state')['sections'][0])

    def test_independent_interviews_do_not_share_answers(self):
        with tempfile.TemporaryDirectory() as other:
            directory = Path(other)
            interview.write_json(directory / 'state.json', self.request('state'))
            interview.submit(self.directory, answers())
            self.assertNotIn('answers', interview.read_json(directory / 'state.json')['sections'][0])


class RecoveryTest(unittest.TestCase):
    def test_exact_resume_commands_quote_paths_and_keep_permissions(self):
        directory = Path("/tmp/interview ' $(touch unexpected)")
        cwd = Path("/tmp/project ' with spaces")
        session = '00000000-0000-4000-8000-000000000001'
        for agent in ('codex', 'claude'):
            with self.subTest(agent=agent):
                recovery = interview.recovery_info(directory, agent, session, cwd)
                parts = shlex.split(recovery['resume_command'])
                self.assertEqual(parts[:4], ['cd', '--', str(cwd), '&&'])
                self.assertEqual(parts[4], agent)
                self.assertIn(session, parts)
                self.assertIn(recovery['prompt'], parts)
                self.assertEqual(shlex.split(recovery['read_command'])[-1], str(directory))
                if agent == 'codex':
                    self.assertEqual(parts[parts.index('-s') + 1], 'workspace-write')
                    self.assertEqual(parts[parts.index('-a') + 1], 'on-request')
                else:
                    self.assertEqual(parts[parts.index('--permission-mode') + 1], 'manual')
                    self.assertTrue(json.loads(parts[parts.index('--settings') + 1])['sandbox']['enabled'])

    def test_unknown_session_uses_picker_and_separate_prompt(self):
        for agent in ('codex', 'claude'):
            recovery = interview.recovery_info(Path('/tmp/interview'), agent, None, Path('/tmp/project'))
            self.assertFalse(recovery['exact_session'])
            parts = shlex.split(recovery['resume_command'])
            self.assertNotIn('--last', parts)
            self.assertNotIn('--continue', parts)
            self.assertNotIn(recovery['prompt'], parts)
            self.assertIn('read', recovery['prompt'])

    def test_unexpanded_claude_placeholder_is_rejected(self):
        with self.assertRaises(ValueError):
            interview.recovery_info(Path('/tmp/interview'), 'claude', '${CLAUDE_SESSION_ID}', Path('/tmp'))


if __name__ == '__main__':
    unittest.main()
