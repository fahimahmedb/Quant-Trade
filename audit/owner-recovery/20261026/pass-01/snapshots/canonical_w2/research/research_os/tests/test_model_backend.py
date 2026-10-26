import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import unittest

from research.research_os.model_backend import (
    BackendUnavailable, GPTOSSBackend, InvalidModelOutput, LocalHTTPBackend,
    ModelBudget, validate_structure,
)

SCHEMA = {'type': 'object', 'properties': {'critique': {'type': 'string'}},
          'required': ['critique'], 'additionalProperties': False}


class BackendTests(unittest.TestCase):
    def setUp(self):
        self.calls, self.response = [], {'message': {'content': '{"critique":"No outcome evidence."}'}, 'done': True}
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                outer.calls.append((self.path, None))
                self.send_response(200)
                self.end_headers()
                self.wfile.write(json.dumps({'models': [{'name': 'gpt-oss:test'}]}).encode())

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                outer.calls.append((self.path, body))
                self.send_response(200)
                self.end_headers()
                result = {'details': {'family': 'gptoss', 'quantization_level': 'TEST'}} if self.path == '/api/show' else outer.response
                self.wfile.write(json.dumps(result).encode())

        self.server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.backend = GPTOSSBackend(endpoint=f'http://127.0.0.1:{self.server.server_port}',
                                     model='gpt-oss:test', runtime='ollama', budget=ModelBudget(timeout_seconds=1, retries=0))

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def test_local_health_and_structured_output_no_variant_hardcode(self):
        health = self.backend.healthcheck()
        self.assertEqual(health['details']['family'], 'gptoss')
        self.assertEqual(self.backend.generate_structured('Critique the supplied claim.', SCHEMA),
                         {'critique': 'No outcome evidence.'})
        payload = self.calls[-1][1]
        self.assertEqual(payload['model'], 'gpt-oss:test')
        self.assertEqual(payload['options']['temperature'], 0)
        self.assertFalse(payload['stream'])
        self.assertEqual(payload['think'], 'low')

    def test_hosted_endpoints_proxy_credentials_and_redirect_destinations_refused(self):
        for endpoint in ('https://api.openai.com:443', 'http://example.com:80',
                         'http://user:secret@127.0.0.1:11434', 'http://127.0.0.1:11434/v1',
                         'http://169.254.169.254:80'):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                LocalHTTPBackend(endpoint=endpoint, model='anything', runtime='ollama')

    def test_invalid_or_truncated_model_output_is_not_fabricated(self):
        for content in ('not json', '{"critique":"x","authority":true}', '{"critique":13}'):
            self.response['message']['content'] = content
            with self.assertRaises(InvalidModelOutput):
                self.backend.generate_structured('test', SCHEMA)
        self.response['done_reason'] = 'length'
        with self.assertRaises(InvalidModelOutput):
            self.backend.generate_text('test')

    def test_context_and_retry_budgets_are_hard_limits(self):
        with self.assertRaises(BackendUnavailable):
            self.backend.generate_text('x' * 10000)
        self.assertEqual(self.calls, [])
        with self.assertRaises(ValueError):
            ModelBudget(retries=10)
        with self.assertRaises(ValueError):
            ModelBudget(timeout_seconds=1000)

    def test_unavailable_backend_reports_error_without_external_fallback(self):
        self.backend.endpoint = 'http://127.0.0.1:1'
        with self.assertRaises(BackendUnavailable):
            self.backend.generate_text('test')
        self.assertEqual(self.calls, [])

    def test_schema_boolean_cannot_satisfy_integer(self):
        with self.assertRaises(InvalidModelOutput):
            validate_structure(True, {'type': 'integer'})


if __name__ == '__main__':
    unittest.main()
