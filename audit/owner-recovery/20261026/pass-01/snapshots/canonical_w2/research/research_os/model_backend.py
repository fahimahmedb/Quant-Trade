"""Pluggable, local-only reasoning. No credentials, hosted fallback or tools.

The worker depends on ModelBackend, not an inference runtime or model variant.
Model output is untrusted research commentary, never evidence or authority.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import ipaddress
import json
import socket
import time
from urllib.parse import urlsplit
import urllib.error
import urllib.request


class BackendUnavailable(RuntimeError):
    pass


class InvalidModelOutput(BackendUnavailable):
    pass


@dataclass(frozen=True)
class ModelBudget:
    timeout_seconds: float = 120
    retries: int = 1
    context_tokens: int = 8192
    output_tokens: int = 768
    temperature: float = 0
    seed: int = 19

    def __post_init__(self):
        if not (0 < self.timeout_seconds <= 240 and 0 <= self.retries <= 2
                and 256 <= self.output_tokens < self.context_tokens <= 32768
                and 0 <= self.temperature <= 1):
            raise ValueError('INVALID_MODEL_BUDGET')


class ModelBackend(ABC):
    @abstractmethod
    def healthcheck(self) -> dict:
        """Return a measured status, or raise BackendUnavailable."""

    @abstractmethod
    def generate_structured(self, prompt: str, schema: dict) -> dict:
        pass

    @abstractmethod
    def generate_text(self, prompt: str) -> str:
        pass


def validate_structure(value, schema):
    """Strict JSON subset used by the worker's bounded reasoning contracts."""
    types = {'object': dict, 'array': list, 'string': str, 'boolean': bool,
             'integer': int, 'number': (int, float), 'null': type(None)}
    kind = schema.get('type')
    if kind not in types:
        raise InvalidModelOutput('UNSUPPORTED_OUTPUT_SCHEMA')
    if not isinstance(value, types[kind]) or (kind in ('integer', 'number') and isinstance(value, bool)):
        raise InvalidModelOutput('MODEL_OUTPUT_TYPE_MISMATCH')
    if 'enum' in schema and value not in schema['enum']:
        raise InvalidModelOutput('MODEL_OUTPUT_ENUM_MISMATCH')
    if kind == 'object':
        if set(schema.get('required', [])) - value.keys():
            raise InvalidModelOutput('MODEL_OUTPUT_REQUIRED_FIELD_MISSING')
        properties = schema.get('properties', {})
        if schema.get('additionalProperties') is False and value.keys() - properties.keys():
            raise InvalidModelOutput('MODEL_OUTPUT_UNDECLARED_FIELD')
        for key in value.keys() & properties.keys():
            validate_structure(value[key], properties[key])
    elif kind == 'array':
        if not schema.get('minItems', 0) <= len(value) <= schema.get('maxItems', 32):
            raise InvalidModelOutput('MODEL_OUTPUT_ARRAY_BUDGET')
        for item in value:
            validate_structure(item, schema['items'])
    elif kind == 'string':
        if not schema.get('minLength', 0) <= len(value) <= schema.get('maxLength', 12000):
            raise InvalidModelOutput('MODEL_OUTPUT_TEXT_BUDGET')


class LocalHTTPBackend(ModelBackend):
    def __init__(self, *, endpoint: str, model: str, runtime: str, budget: ModelBudget | None = None):
        parsed = urlsplit(endpoint)
        try:
            loopback = ipaddress.ip_address(parsed.hostname or '').is_loopback
        except ValueError:
            loopback = False
        if not (parsed.scheme == 'http' and loopback and parsed.port
                and not parsed.username and not parsed.password and parsed.path in ('', '/')
                and not parsed.query and not parsed.fragment):
            raise ValueError('MODEL_ENDPOINT_MUST_BE_EXPLICIT_LOOPBACK_HTTP')
        if runtime not in ('ollama', 'openai_compatible') or not model or len(model) > 256:
            raise ValueError('EXPLICIT_LOCAL_RUNTIME_AND_MODEL_REQUIRED')
        self.endpoint, self.model, self.runtime = endpoint.rstrip('/'), model, runtime
        self.budget = budget or ModelBudget()

    def _runtime_reasoning_options(self):
        return {}

    def _request(self, path, payload=None, *, timeout=None):
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *args, **kwargs):
                return None
        raw = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(self.endpoint + path, data=raw,
                                         headers={'Content-Type': 'application/json'})
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
        for attempt in range(self.budget.retries + 1):
            try:
                with opener.open(request, timeout=min(timeout or self.budget.timeout_seconds, self.budget.timeout_seconds)) as response:
                    data = response.read(2 * 1024 * 1024 + 1)
                if len(data) > 2 * 1024 * 1024:
                    raise InvalidModelOutput('LOCAL_MODEL_RESPONSE_TOO_LARGE')
                decoded = json.loads(data, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
                if not isinstance(decoded, dict):
                    raise InvalidModelOutput('LOCAL_MODEL_RESPONSE_NOT_OBJECT')
                return decoded
            except urllib.error.HTTPError as exc:
                if exc.code < 500 or attempt == self.budget.retries:
                    raise BackendUnavailable(f'LOCAL_MODEL_HTTP_{exc.code}') from None
            except (OSError, socket.timeout, ValueError) as exc:
                if attempt == self.budget.retries:
                    raise BackendUnavailable(f'LOCAL_MODEL_REQUEST_FAILED:{type(exc).__name__}') from None
            time.sleep(0.2 * (attempt + 1))
        raise BackendUnavailable('LOCAL_MODEL_RETRIES_EXHAUSTED')

    def healthcheck(self):
        data = self._request('/api/tags' if self.runtime == 'ollama' else '/v1/models', timeout=5)
        models = data.get('models', []) if self.runtime == 'ollama' else data.get('data', [])
        if not isinstance(models, list) or any(not isinstance(m, dict) for m in models):
            raise InvalidModelOutput('LOCAL_MODEL_LIST_INVALID')
        matches = [m for m in models if m.get('name', m.get('id')) == self.model]
        if not matches:
            raise BackendUnavailable('CONFIGURED_LOCAL_MODEL_NOT_PRESENT')
        return {'status': 'PASS', 'runtime': self.runtime, 'model': self.model,
                'local_only': True, 'metadata': matches[0]}

    def _generate(self, prompt, schema=None):
        # UTF-8 bytes give a conservative bound without a model-specific tokenizer.
        cost = len(prompt.encode()) + (len(json.dumps(schema).encode()) if schema else 0)
        if cost > self.budget.context_tokens - self.budget.output_tokens - 256:
            raise BackendUnavailable('MODEL_CONTEXT_BUDGET_EXCEEDED')
        if self.runtime == 'ollama':
            payload = {'model': self.model, 'messages': [{'role': 'user', 'content': prompt}],
                       'stream': False, 'keep_alive': '5m',
                       'options': {'num_ctx': self.budget.context_tokens, 'num_predict': self.budget.output_tokens,
                                   'temperature': self.budget.temperature, 'seed': self.budget.seed}}
            if schema:
                payload['format'] = schema
            payload.update(self._runtime_reasoning_options())
            data = self._request('/api/chat', payload)
            if data.get('done') is not True or data.get('done_reason') == 'length':
                raise InvalidModelOutput('MODEL_OUTPUT_INCOMPLETE')
            message = data.get('message')
            result = message.get('content') if isinstance(message, dict) else None
        else:
            payload = {'model': self.model, 'messages': [{'role': 'user', 'content': prompt}],
                       'stream': False, 'max_tokens': self.budget.output_tokens,
                       'temperature': self.budget.temperature, 'seed': self.budget.seed}
            if schema:
                payload['response_format'] = {'type': 'json_schema', 'json_schema': {
                    'name': 'research_reasoning', 'strict': True, 'schema': schema}}
            payload.update(self._runtime_reasoning_options())
            data = self._request('/v1/chat/completions', payload)
            choices = data.get('choices') or []
            if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict) or choices[0].get('finish_reason') != 'stop':
                raise InvalidModelOutput('MODEL_OUTPUT_INCOMPLETE')
            message = choices[0].get('message')
            result = message.get('content') if isinstance(message, dict) else None
        if not isinstance(result, str) or not result.strip():
            raise InvalidModelOutput('MODEL_OUTPUT_EMPTY')
        return result

    def generate_text(self, prompt):
        return self._generate(prompt)

    def generate_structured(self, prompt, schema):
        result = self._generate(prompt, schema)
        try:
            value = json.loads(result, parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
        except (ValueError, TypeError):
            raise InvalidModelOutput('MODEL_OUTPUT_NOT_JSON') from None
        validate_structure(value, schema)
        return value


class GPTOSSBackend(LocalHTTPBackend):
    """GPT-OSS/variant adapter; variant and quantization come from VM inventory."""
    def _runtime_reasoning_options(self):
        return {'think': 'low'} if self.runtime == 'ollama' else {'reasoning_effort': 'low'}

    def healthcheck(self):
        health = super().healthcheck()
        if self.runtime == 'ollama':
            details = self._request('/api/show', {'model': self.model}, timeout=5)
            metadata = details.get('details') or {}
            family = str(metadata.get('family', '')).lower().replace('_', '-').replace('gptoss', 'gpt-oss')
            if family != 'gpt-oss':
                raise BackendUnavailable('GPT_OSS_ARCHITECTURE_NOT_CONFIRMED')
            health['details'] = metadata
        elif 'gpt-oss' not in self.model.lower().replace('_', '-'):
            raise BackendUnavailable('GPT_OSS_MODEL_ID_NOT_CONFIRMED')
        return health
