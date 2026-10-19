#!/usr/bin/env python3
"""Read-only, bounded inventory. Run ON the Oracle VM before any model install.

Never reads environment, credentials, process command lines or service ExecStart.
No model download, model load, inference, service change or package installation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time
import urllib.request


def command(args):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=8)
        return {"returncode": p.returncode, "stdout": p.stdout[:16000]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"unavailable": type(exc).__name__}


def local_json(url, payload=None):
    # Explicit proxy bypass ONLY for loopback. Never follows redirects.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *args, **kwargs):
            return None
    try:
        request = urllib.request.Request(url, data=json.dumps(payload).encode() if payload else None,
                                         headers={"Content-Type": "application/json"})
        with urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect()).open(request, timeout=5) as r:
            raw = r.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            return {"unavailable": "RESPONSE_TOO_LARGE"}
        return json.loads(raw)
    except (OSError, ValueError) as exc:
        return {"unavailable": type(exc).__name__}


def processes():
    found = []
    for proc in Path('/proc').glob('[0-9]*'):
        try:
            name = (proc / 'comm').read_text().strip()
            if not any(key in name.lower() for key in ('ollama', 'llama', 'gpt', 'vllm')):
                continue
            status = dict(line.split(':', 1) for line in (proc / 'status').read_text().splitlines() if ':' in line)
            stat1 = (proc / 'stat').read_text().rsplit(')', 1)[1].split()
            ticks1 = int(stat1[11]) + int(stat1[12])
            start = time.monotonic()
            time.sleep(0.1)
            stat2 = (proc / 'stat').read_text().rsplit(')', 1)[1].split()
            ticks2 = int(stat2[11]) + int(stat2[12])
            found.append({"pid": int(proc.name), "name": name,
                          "executable": str((proc / 'exe').resolve()),
                          "rss": status.get('VmRSS', '').strip(), "swap": status.get('VmSwap', '').strip(),
                          "cpu_one_core_percent_sample": round(100 * (ticks2 - ticks1) / os.sysconf('SC_CLK_TCK') / (time.monotonic() - start), 2)})
        except (OSError, ValueError, IndexError):
            continue
    return found


def inventory(model_roots):
    tags = local_json('http://127.0.0.1:11434/api/tags')
    models = []
    for model in (tags.get('models') or [])[:32]:
        name = model.get('name', '')
        entry = {k: model.get(k) for k in ('name', 'digest', 'size', 'details', 'modified_at')}
        if 'gpt-oss' in name.lower() or 'gptoss' in name.lower():
            details = local_json('http://127.0.0.1:11434/api/show', {'model': name})
            # Deliberately exclude modelfile/template/system text (may contain secrets).
            entry['metadata'] = {k: details.get(k) for k in ('details', 'model_info', 'capabilities')}
        models.append(entry)
    files, truncated = [], False
    for root in model_roots:
        root = Path(root).expanduser()
        if not root.is_dir():
            continue
        for directory, dirs, names in os.walk(root, followlinks=False):
            if len(Path(directory).relative_to(root).parts) > 5:
                dirs[:] = []
                continue
            for name in names:
                path = Path(directory) / name
                if path.is_symlink() or not (name.lower().endswith(('.gguf', '.safetensors')) or 'gpt-oss' in str(path).lower()):
                    continue
                try:
                    files.append({'path': str(path), 'size_bytes': path.stat().st_size})
                except OSError:
                    continue
                if len(files) >= 100:
                    truncated = True
                    break
            if truncated:
                break
        if truncated:
            break
    disk = shutil.disk_usage('/')
    return {'schema_version': 'oracle-local-model-inventory-v1',
            'observed_at': datetime.now(timezone.utc).isoformat(), 'evidence_scope': 'LIVE_HOST_WHERE_EXECUTED',
            'host_architecture': platform.machine(), 'kernel': platform.release(), 'cpu_count': os.cpu_count(),
            'memory': command(['free', '-b']), 'disk': {'total': disk.total, 'free': disk.free},
            'cpu': command(['lscpu']), 'processes': processes(),
            'runtimes': {name: command([name, '--version']) for name in ('ollama', 'llama-server', 'llama-cli') if shutil.which(name)},
            'services': {name: command(['systemctl', 'show', name, '--property=ActiveState,SubState,UnitFileState,MainPID,MemoryCurrent,CPUUsageNSec,FragmentPath']) for name in ('ollama.service', 'llama-server.service', 'gpt-oss.service', 'quant-research-worker.timer')},
            'ollama_models': models, 'ollama_status': tags.get('unavailable', 'REACHABLE'),
            'loaded_models': local_json('http://127.0.0.1:11434/api/ps'),
            'openai_compatible_models': local_json('http://127.0.0.1:8080/v1/models'),
            'llama_properties': local_json('http://127.0.0.1:8080/props'),
            'model_files': files, 'file_scan_truncated': truncated,
            'compatibility_verdict': 'REQUIRES_REVIEW_AND_BOUNDED_INFERENCE_CANARY',
            'mutations_performed': False, 'models_downloaded': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model-root', action='append', default=[])
    args = parser.parse_args()
    roots = args.model_root or ['/var/lib/ollama', '/usr/share/ollama/.ollama/models', '/opt/models', str(Path.home() / '.ollama/models')]
    print(json.dumps(inventory(roots), indent=2, sort_keys=True))
