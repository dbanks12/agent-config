#!/usr/bin/env python3
"""Local browser interviews. Uses Python's standard library on Linux and macOS."""
import argparse
from contextlib import contextmanager
import fcntl
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import secrets
import shlex
import subprocess
import sys
import threading
import time
from urllib.request import Request, urlopen
import webbrowser
import uuid

ASSETS = Path(__file__).resolve().parents[1] / 'assets'


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    os.chmod(temp, 0o600)
    temp.replace(path)


def save_state(directory, state):
    write_json(directory / 'state.json', state)
    lines = [f"# {state['title']}", '']
    for section in state['sections']:
        lines.extend([f"## {section['title']}", ''])
        for question in section['questions']:
            lines.extend([f"### {question['title']}", '', question['body'], '',
                          'Recommendation:', question['recommendation'], ''])
            answer = section.get('answers', {}).get(question['id'])
            if answer:
                lines.extend(['Accepted recommendation:' if answer['mode'] == 'accepted' else 'Your response:', answer['text'], ''])
                if answer.get('notes'):
                    lines.extend(['Your notes:', answer['notes'], ''])
            else:
                lines.extend(['Awaiting your response.', ''])
    if state.get('summary'):
        lines.extend(['## Shared understanding', '', state['summary'], ''])
    temp = directory / 'answers.md.tmp'
    temp.write_text('\n'.join(lines))
    os.chmod(temp, 0o600)
    temp.replace(directory / 'answers.md')


def recovery_info(directory, agent, session_id, cwd):
    if session_id:
        session_id = str(uuid.UUID(session_id))
    helper = [sys.executable, str(Path(__file__).resolve())]
    read_command = shlex.join(helper + ['read', '--dir', str(directory)])
    restart_command = shlex.join(helper + ['start', '--dir', str(directory), '--open'])
    prompt = (f'Resume the grill-me-html interview stored at {directory}. '
              f'Read {Path(__file__).resolve().parents[1] / "SKILL.md"}. '
              f'Recover submitted answers with:\n{read_command}\n'
              'Use the saved answers to continue the design tree. '
              'Restart the page server with the same directory if necessary. '
              'Wait for any unanswered section or publish the next frontier. '
              'Do not start a new interview.')
    if agent == 'codex':
        command = ['codex', 'resume', '-s', 'workspace-write', '-a', 'on-request', '--add-dir', str(directory)]
    else:
        command = ['claude', '--permission-mode', 'manual', '--settings', '{"sandbox":{"enabled":true}}',
                   '--add-dir', str(directory), '--resume']
    if session_id:
        command.extend([session_id, prompt])
    return {
        'agent': agent, 'session_id': session_id, 'exact_session': bool(session_id),
        'resume_command': f'cd -- {shlex.quote(str(cwd))} && {shlex.join(command)}',
        'prompt': prompt, 'read_command': read_command, 'restart_command': restart_command,
        'answers_path': str(directory / 'state.json'), 'transcript_path': str(directory / 'answers.md'),
    }


@contextmanager
def locked(directory):
    with (directory / 'lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_section(section):
    if not isinstance(section, dict) or not all(nonempty(section.get(k)) for k in ('id', 'title')):
        raise ValueError('A section needs a nonempty id and title.')
    questions = section.get('questions')
    if not isinstance(questions, list) or not questions:
        raise ValueError('A section needs at least one question.')
    ids = set()
    for q in questions:
        if not isinstance(q, dict) or not all(nonempty(q.get(k)) for k in ('id', 'title', 'body', 'recommendation')):
            raise ValueError('Each question needs an id, title, body, and recommendation.')
        if q['id'] in ids:
            raise ValueError('Question ids must be unique within a section.')
        ids.add(q['id'])
    remaining = section.get('remaining')
    if not isinstance(remaining, dict) or any(type(remaining.get(k)) is not int for k in ('min', 'max')):
        raise ValueError('Remaining questions need integer min and max estimates.')
    if not 0 <= remaining['min'] <= remaining['max']:
        raise ValueError('Remaining estimates must satisfy 0 <= min <= max.')
    return {k: section[k] for k in ('id', 'title', 'questions', 'remaining')}


def publish(directory, section):
    section = validate_section(section)
    with locked(directory):
        state = read_json(directory / 'state.json')
        if state['finished']:
            raise ValueError('This interview is complete.')
        if any(s['id'] == section['id'] for s in state['sections']):
            raise ValueError('Use a new section id. Published sections are immutable.')
        if any('answers' not in s for s in state['sections']):
            raise ValueError('Wait for the current section answers before publishing another section.')
        state['remaining'] = section.pop('remaining')
        state['sections'].append(section)
        save_state(directory, state)
        return state


def submit(directory, payload):
    if not isinstance(payload, dict):
        raise ValueError('Send an object with section and answers fields.')
    with locked(directory):
        state = read_json(directory / 'state.json')
        section = next((s for s in state['sections'] if s['id'] == payload.get('section')), None)
        if section is None:
            raise ValueError('Unknown section.')
        answers = payload.get('answers')
        if not isinstance(answers, dict) or set(answers) != {q['id'] for q in section['questions']}:
            raise ValueError('Answer every question in the section.')
        normalized = {}
        for q in section['questions']:
            answer = answers[q['id']]
            if not isinstance(answer, dict) or answer.get('mode') not in ('accepted', 'custom'):
                raise ValueError('Each answer needs an accepted or custom mode.')
            value = q['recommendation'] if answer['mode'] == 'accepted' else answer.get('text')
            if not nonempty(value):
                raise ValueError('Custom answers must contain text.')
            normalized[q['id']] = {'mode': answer['mode'], 'text': value}
            if 'notes' in answer:
                if answer['mode'] != 'accepted' or not isinstance(answer['notes'], str):
                    raise ValueError('Notes must contain text attached to an accepted recommendation.')
                if answer['notes'].strip():
                    normalized[q['id']]['notes'] = answer['notes']
        if 'answers' in section:
            if section['answers'] != normalized:
                raise ValueError('This section is already submitted. Ask the agent to reopen the decision in a new section.')
            return state  # Retrying a completed request is safe.
        if state['finished']:
            raise ValueError('This interview is complete.')
        section['answers'] = normalized
        save_state(directory, state)
        return state


def make_server(directory, token):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass  # Keep the URL token and user responses out of request logs.

        def send(self, code, content, mime='application/json'):
            data = json.dumps(content, ensure_ascii=False).encode() if mime == 'application/json' else content
            self.send_response(code)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
            self.end_headers()
            self.wfile.write(data)

        def authorized_path(self):
            expected = f'127.0.0.1:{self.server.server_port}'
            origin = self.headers.get('Origin')
            if self.headers.get('Host') != expected or (origin and origin != f'http://{expected}'):
                self.send(403, {'error': 'This request must come from the local interview page.'})
                return None
            prefix = f'/{token}/'
            if not self.path.startswith(prefix):
                self.send(404, {'error': 'Unknown interview URL.'})
                return None
            return self.path[len(prefix):]

        def do_GET(self):
            path = self.authorized_path()
            if path is None:
                return
            if path == 'state':
                self.send(200, read_json(directory / 'state.json'))
            elif path in ('', 'app.js'):
                asset = ASSETS / ('index.html' if path == '' else path)
                self.send(200, asset.read_bytes(), 'text/html; charset=utf-8' if path == '' else 'text/javascript; charset=utf-8')
            else:
                self.send(404, {'error': 'Unknown resource.'})

        def do_POST(self):
            path = self.authorized_path()
            if path is None:
                return
            if path not in ('answers', 'stop'):
                self.send(404, {'error': 'Unknown resource.'})
                return
            try:
                size = int(self.headers.get('Content-Length', '0'))
                if not 0 < size <= 1024 * 1024:
                    raise ValueError('The request must contain at most 1 MiB of JSON.')
                if self.headers.get('Content-Type') != 'application/json':
                    raise ValueError('Send the request as application/json.')
                payload = json.loads(self.rfile.read(size))
                if path == 'answers':
                    self.send(200, submit(directory, payload))
                else:
                    self.send(200, {'status': 'stopped'})
                    threading.Thread(target=self.server.shutdown, daemon=True).start()
            except (ValueError, UnicodeDecodeError) as error:
                self.send(400, {'error': str(error)})

    return ThreadingHTTPServer(('127.0.0.1', 0), Handler)


def serve(directory):
    # Only one server can own a directory, including concurrent start attempts.
    with (directory / 'server.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        config = read_json(directory / 'connection.json')
        server = make_server(directory, config['token'])
        config['url'] = f"http://127.0.0.1:{server.server_port}/{config['token']}/"
        write_json(directory / 'connection.json', config)
        try:
            server.serve_forever()
        finally:
            server.server_close()


def running_url(directory):
    config = read_json(directory / 'connection.json')
    url = config.get('url')
    if url:
        try:
            with urlopen(url + 'state', timeout=1) as response:
                if response.status == 200:
                    return url
        except OSError:
            pass
    return None


def start(directory, title, open_browser, agent=None, session_id=None, cwd=None):
    if directory.exists() and any(directory.iterdir()) and not (directory / 'state.json').is_file():
        raise ValueError('Use an empty directory or an existing interview directory.')
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    os.chmod(directory, 0o700)
    with locked(directory):
        if not (directory / 'state.json').exists():
            if agent not in ('codex', 'claude'):
                raise ValueError('A new interview needs --agent codex or --agent claude.')
            if agent == 'codex' and not session_id:
                session_id = os.environ.get('CODEX_THREAD_ID') or os.environ.get('CODEX_SESSION_ID')
            recovery = recovery_info(directory, agent, session_id, cwd or Path.cwd())
            save_state(directory, {'title': title, 'sections': [], 'remaining': None, 'finished': False, 'recovery': recovery})
            (directory / 'resume.txt').write_text(
                'Resume the launching session:\n' + recovery['resume_command'] +
                '\n\nIf the command opens a picker, select the original session and paste:\n' + recovery['prompt'] +
                '\n\nRestart the page server:\n' + recovery['restart_command'] + '\n')
            os.chmod(directory / 'resume.txt', 0o600)
        if not (directory / 'connection.json').exists():
            write_json(directory / 'connection.json', {'token': secrets.token_urlsafe(32)})
    url = running_url(directory)
    if not url:
        with (directory / 'server.log').open('a') as log:
            process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'serve', '--dir', str(directory)],
                                       stdin=subprocess.DEVNULL, stdout=log, stderr=log, start_new_session=True)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            url = running_url(directory)
            if url:
                break
            if process.poll() is not None:
                raise ValueError(f'Server startup failed. Read {directory / "server.log"}.')
            time.sleep(0.1)
        if not url:
            process.terminate()
            raise ValueError(f'Server startup timed out. Read {directory / "server.log"}.')
    result = {'url': url, 'directory': str(directory)}
    if open_browser:
        result['browser_opened'] = webbrowser.open(url)
    return result


def wait_for_answers(directory, section_id, timeout):
    deadline = time.monotonic() + timeout
    while True:
        state = read_json(directory / 'state.json')
        section = next((s for s in state['sections'] if s['id'] == section_id), None)
        if section is None:
            raise ValueError('Unknown section.')
        if 'answers' in section:
            return {'status': 'answered', 'section': section}
        if time.monotonic() >= deadline:
            return {'status': 'waiting', 'section': section_id}
        time.sleep(0.25)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ('start', 'serve', 'publish', 'wait', 'read', 'finish', 'stop'):
        command = commands.add_parser(name)
        command.add_argument('--dir', type=Path, required=True, help='Private directory for this interview')
        if name == 'start':
            command.add_argument('--title', default='Make the next decision.')
            command.add_argument('--agent', choices=('codex', 'claude'), help='Launching agent, required for new interviews')
            command.add_argument('--session-id', help='Exact launching session UUID')
            command.add_argument('--cwd', type=Path, default=Path.cwd(), help='Original project directory')
            command.add_argument('--open', action='store_true', help='Open the local page in the default browser')
        elif name == 'publish':
            command.add_argument('--file', type=Path, required=True, help='Section JSON file')
        elif name == 'wait':
            command.add_argument('--section', required=True)
            command.add_argument('--timeout', type=int, choices=range(1, 61), default=45, metavar='1..60')
        elif name == 'finish':
            command.add_argument('--file', type=Path, required=True, help='Plain text summary file')
    args = parser.parse_args()
    directory = args.dir.resolve()
    try:
        if args.command == 'start':
            result = start(directory, args.title, args.open, args.agent, args.session_id, args.cwd.resolve())
        elif args.command == 'serve':
            serve(directory)
            return
        elif args.command == 'publish':
            state = publish(directory, read_json(args.file))
            result = {'status': 'published', 'section': state['sections'][-1]['id']}
        elif args.command == 'wait':
            result = wait_for_answers(directory, args.section, args.timeout)
        elif args.command == 'read':
            result = read_json(directory / 'state.json')
        elif args.command == 'finish':
            summary = args.file.read_text()
            if not nonempty(summary):
                raise ValueError('The completion summary must contain text.')
            with locked(directory):
                state = read_json(directory / 'state.json')
                if not state['sections'] or any('answers' not in s for s in state['sections']):
                    raise ValueError('Complete all published sections before finishing.')
                state.update(finished=True, summary=summary, remaining={'min': 0, 'max': 0})
                save_state(directory, state)
            result = {'status': 'finished'}
        else:
            url = running_url(directory)
            if url:
                with urlopen(Request(url + 'stop', data=b'{}', headers={'Content-Type': 'application/json'}), timeout=3) as response:
                    response.read()
            result = {'status': 'stopped'}
        print(json.dumps(result, ensure_ascii=False), flush=True)
    except (OSError, ValueError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
