"""Exercise the actual PHP endpoint; no SMTP credentials or email delivery."""
import http.cookiejar
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PHP = shutil.which('php') or '/workspace/tooling/php/usr/bin/php8.4'

class ContactSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='glm-contact-')
        env = os.environ.copy()
        env['LD_LIBRARY_PATH'] = '/workspace/tooling/php/usr/lib/x86_64-linux-gnu' + (':' + env['LD_LIBRARY_PATH'] if env.get('LD_LIBRARY_PATH') else '')
        env['GLM_RATE_DIR'] = cls.temp.name + '/rates'
        # Do not inherit real SMTP credentials in automated tests.
        for key in list(env):
            if key.startswith('GLM_SMTP_') or key in ['GLM_FROM_EMAIL', 'GLM_TO_EMAIL']:
                del env[key]
        if (ROOT / 'private/config.php').exists():
            raise RuntimeError('Use an isolated checkout without real mail config for smoke tests.')
        Path(cls.temp.name + '/sessions').mkdir(mode=0o700)
        cls.log = open(cls.temp.name + '/server.log', 'w+')
        cls.server = subprocess.Popen([PHP, '-d', 'session.save_path=' + cls.temp.name + '/sessions', '-S', '127.0.0.1:8091', '-t', str(ROOT / 'public')], env=env, stdout=cls.log, stderr=cls.log)
        for _ in range(50):
            try:
                urllib.request.urlopen('http://127.0.0.1:8091/contact.php', timeout=1).close()
                break
            except (OSError, urllib.error.URLError):
                if cls.server.poll() is not None: raise RuntimeError('Test server did not start')
                time.sleep(.1)
        else: raise RuntimeError('Test server never became ready')

    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait(timeout=5)
        cls.log.close()
        cls.temp.cleanup()

    def setUp(self):
        for file in Path(self.temp.name).glob('rates/*.json'): file.unlink()
        self.client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        code, data = self.request()
        self.assertEqual(code, 200)
        self.assertFalse(data['ready'])
        self.token = data['csrf']

    def request(self, fields=None, method=None):
        body = urllib.parse.urlencode(fields).encode() if fields is not None else None
        req = urllib.request.Request('http://127.0.0.1:8091/contact.php', body, method=method)
        try: response = self.client.open(req, timeout=10)
        except urllib.error.HTTPError as e: response = e
        with response:
            self.assertIn('no-store', response.headers.get('Cache-Control', ''))
            return response.status, json.load(response)

    def valid(self, **overrides):
        return dict(name='Test Visitor', email='visitor@example.com', message='A representative test inquiry.', website='', csrf=self.token, **overrides)

    def test_no_credentials_never_claims_delivery(self):
        code, data = self.request(self.valid())
        self.assertEqual(code, 503)
        self.assertIn('has not been sent', data['message'])

    def test_csrf_required(self):
        fields = self.valid(); fields['csrf'] = 'wrong'
        self.assertEqual(self.request(fields)[0], 403)

    def test_invalid_email(self):
        fields = self.valid(); fields['email'] = 'not-an-email'
        self.assertEqual(self.request(fields)[0], 422)

    def test_header_injection(self):
        fields = self.valid(); fields['name'] = 'Visitor\r\nBcc: bad@example.com'
        self.assertEqual(self.request(fields)[0], 422)

    def test_honeypot(self):
        fields = self.valid(); fields['website'] = 'spam'
        self.assertEqual(self.request(fields)[0], 422)

    def test_short_message(self):
        fields = self.valid(); fields['message'] = 'short'
        self.assertEqual(self.request(fields)[0], 422)

    def test_array_input(self):
        fields = self.valid(); del fields['name']; fields['name[]'] = 'bad'
        self.assertEqual(self.request(fields)[0], 422)

    def test_oversized_request(self):
        fields = self.valid(); fields['message'] = 'x' * 21000
        self.assertEqual(self.request(fields)[0], 413)

    def test_rate_limit_survives_new_session(self):
        for _ in range(5): self.assertEqual(self.request(self.valid())[0], 503)
        self.client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        _, data = self.request(); self.token = data['csrf']
        self.assertEqual(self.request(self.valid())[0], 429)

    def test_method_rejected(self):
        self.assertEqual(self.request(method='PUT')[0], 405)

if __name__ == '__main__': unittest.main(verbosity=2)
