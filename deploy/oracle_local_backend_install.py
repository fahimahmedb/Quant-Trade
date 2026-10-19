#!/usr/bin/env python3
"""Stage one pinned CPU runtime and one pinned local model, without services.

This is BUILD-plane installation only. Normal Research OS wakes never download
models, run this installer, or depend on a particular publisher or variant.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request

RUNTIME = {
    'version': 'llama.cpp-b11742',
    'source_commit': '4c3c5810f87efe177949f1b85ae509d38a2a311f',
    'url': 'https://github.com/ggml-org/llama.cpp/releases/download/b11742/llama-b11742-bin-ubuntu-arm64.tar.gz',
    'size': 14054733,
    'sha256': '263700393b5a0f3547ca313ef6040c25482b569dc6aa387bf5a8ecb9949b159e',
}
MODEL = {
    'repository': 'leeminwaan/gpt-oss-20b-pruned-10.2B-GGUF',
    'revision': '456fa90a60ea5249f26c0c2e5c69aab5a91d4676',
    'file': 'gpt-oss-10b-q4_k_m.gguf',
    'size': 7723072288,
    'sha256': 'f3a19b894d725229f57a80d28014ee6ad3543bcfcd5dd4496f7b3599e169d240',
    'base_model': 'openai/gpt-oss-20b',
    'pruned_source': 'AmanPriyanshu/gpt-oss-10.2b-specialized-all-pruned-moe-only-14-experts',
    'source_revision': 'a6f98493c58e134ac44b4d1ed4516d9d2f5704af',
    'architecture': 'GptOssForCausalLM', 'layers': 24, 'experts': 14, 'active_experts': 4,
    'quantization': 'Q4_K_M', 'format': 'GGUF', 'license': 'Apache-2.0',
    'local_alias': 'gpt-oss-10.2b-q4-k-m',
    'quality_status': 'EXPERIMENTAL_REQUIRES_ACTUAL_WORKER_REASONING_CANARIES',
}
MODEL['url'] = f'https://huggingface.co/{MODEL["repository"]}/resolve/{MODEL["revision"]}/{MODEL["file"]}'


def verify(path, spec, *, magic=None):
    if path.is_symlink() or not path.is_file() or path.stat().st_size != spec['size']:
        raise ValueError('LOCAL_ASSET_SIZE_OR_TYPE_MISMATCH')
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        first = True
        while chunk := stream.read(8 * 1024 * 1024):
            if first and magic and not chunk.startswith(magic):
                raise ValueError('LOCAL_MODEL_FORMAT_MISMATCH')
            first = False
            digest.update(chunk)
    if digest.hexdigest() != spec['sha256']:
        raise ValueError('LOCAL_ASSET_SHA256_MISMATCH')


def download(path, spec, *, magic=None):
    if path.exists() or path.is_symlink():
        verify(path, spec, magic=magic)
        return 'REUSED_VERIFIED'
    path.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    partial = path.with_suffix(path.suffix + '.part')
    if partial.is_symlink():
        raise ValueError('PARTIAL_ASSET_SYMLINK_FORBIDDEN')
    offset = partial.stat().st_size if partial.exists() else 0
    if offset > spec['size']:
        raise ValueError('PARTIAL_ASSET_TOO_LARGE')
    if shutil.disk_usage(path.parent).free < spec['size'] - offset + 4 * 1024 ** 3:
        raise ValueError('INSUFFICIENT_DISK_HEADROOM_FOR_ONE_MODEL')
    if offset < spec['size']:
        headers = {'User-Agent': 'Quant-Trade pinned local backend installer'}
        if offset:
            headers['Range'] = f'bytes={offset}-'
        request = urllib.request.Request(spec['url'], headers=headers)
        with urllib.request.urlopen(request, timeout=90) as response:
            if offset and (response.status != 206 or not response.headers.get('Content-Range', '').startswith(f'bytes {offset}-')):
                raise ValueError('RESUMABLE_DOWNLOAD_RANGE_NOT_HONORED')
            with partial.open('ab' if partial.exists() else 'xb') as stream:
                os.chmod(partial, 0o600)
                while chunk := response.read(8 * 1024 * 1024):
                    offset += len(chunk)
                    if offset > spec['size']:
                        raise ValueError('REMOTE_ASSET_EXCEEDS_PINNED_SIZE')
                    stream.write(chunk)
                stream.flush()
                os.fsync(stream.fileno())
    verify(partial, spec, magic=magic)
    partial.replace(path)
    return 'DOWNLOADED_AND_VERIFIED'


def stage(base, *, include_model=False):
    if not base.is_absolute():
        raise ValueError('ABSOLUTE_LOCAL_BACKEND_DIRECTORY_REQUIRED')
    base.mkdir(mode=0o700, parents=True, exist_ok=True)
    archive = base / 'assets' / (RUNTIME['sha256'] + '.tar.gz')
    download(archive, RUNTIME)
    runtime = base / 'runtimes' / RUNTIME['sha256']
    runtime.parent.mkdir(mode=0o700, exist_ok=True)
    if not runtime.exists():
        with tempfile.TemporaryDirectory(prefix='.llama-', dir=runtime.parent) as tmp:
            extracted = Path(tmp) / 'runtime'
            extracted.mkdir()
            with tarfile.open(archive, 'r:gz') as tar:
                tar.extractall(extracted, filter='data')
            extracted.rename(runtime)
    binaries = [p for p in runtime.rglob('llama-server') if p.is_file() and not p.is_symlink()]
    if len(binaries) != 1:
        raise ValueError('PINNED_RUNTIME_SERVER_NOT_UNAMBIGUOUS')
    binary = binaries[0]
    version = subprocess.run([str(binary), '--version'], capture_output=True, text=True, timeout=30, check=True)
    help_result = subprocess.run([str(binary), '--help'], capture_output=True, text=True, timeout=30, check=True)
    help_text = help_result.stdout + help_result.stderr
    model = base / 'models' / MODEL['revision'] / MODEL['file']
    report = {'status': 'RUNTIME_STAGED_MODEL_NOT_INSTALLED', 'runtime': dict(RUNTIME, binary=str(binary)),
              'runtime_version_output': (version.stdout + version.stderr)[:2000],
              'supported_flags': [flag for flag in ('--reasoning-budget', '--reasoning-format', '--chat-template-kwargs',
                  '--threads', '--ctx-size', '--no-warmup', '--metrics') if flag in help_text],
              'model': dict(MODEL, path=str(model)), 'services_changed': False, 'scheduler_enabled': False}
    if include_model:
        report['model_installation'] = download(model, MODEL, magic=b'GGUF')
        report['status'] = 'LOCAL_ASSETS_STAGED_NOT_INFERENCE_QUALIFIED'
    receipt = base / 'asset-receipt.json'
    pending = receipt.with_suffix('.tmp')
    pending.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n')
    pending.chmod(0o600)
    pending.replace(receipt)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=Path.home() / 'quant-model')
    parser.add_argument('--model', action='store_true')
    args = parser.parse_args()
    print(json.dumps(stage(args.base, include_model=args.model), sort_keys=True))
