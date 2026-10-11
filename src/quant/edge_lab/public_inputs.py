"""Nonsecret proxy/CA configuration for explicitly pinned public input runners."""
import os
from urllib.parse import urlsplit

from .store import Refused


def runner_environment(protocol, root, environ=None):
    source = os.environ if environ is None else environ
    env = {"PATH": source.get("PATH", "/usr/bin:/bin"), "PYTHONPATH": str(root / "src"),
           "TZ": "UTC", "PYTHONNOUSERSITE": "1", "REAL_CAPITAL_AUTHORIZED": "FALSE",
           "LIVE_TRADING_AUTHORIZED": "FALSE"}
    if not protocol.get("public_inputs"):
        return env
    if protocol["public_inputs"].get("hosts") != ["www.smard.de"]:
        raise Refused("Only the reviewed open SMARD input runner is network-qualified")
    for key in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        value = source.get(key)
        if value:
            parsed = urlsplit(value)
            if (parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username
                    or parsed.password or parsed.query or parsed.fragment or parsed.path not in ("", "/")):
                raise Refused("Authenticated or unqualified proxy cannot be inherited")
            env[key] = value
    for key in ("SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE"):
        if source.get(key):
            env[key] = source[key]
    return env
