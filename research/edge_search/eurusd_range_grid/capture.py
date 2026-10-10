"""Sequential, resumable compressed capture only; never opens ZIP members.

Uses exactly the published HistData pages/free form. No account, mirror or
403 workaround. Complete metadata survives interruption; bytes are reused.
"""
from __future__ import annotations
import base64
from datetime import datetime,timezone
import hashlib
import html
import json
import os
from pathlib import Path
import re
import socket
import time
import urllib.parse
import urllib.request

from run import HERE,CAPTURE,REF,REPO,atomic_json,digest,verify_freeze

UA='quant-research-personal-backtest/0.1'


def active_runs(*,full=True):
    active=[]
    for status in (('in_progress','queued','waiting','pending','requested') if full else ('in_progress',)):
        req=urllib.request.Request('https://api.github.com/repos/'+REPO+
            '/actions/runs?status='+status+'&per_page=100',headers={'User-Agent':UA})
        with urllib.request.urlopen(req,timeout=30) as r:j=json.load(r)
        if j['total_count']:
            active.extend({'id':r['id'],'name':r['name'],'status':r['status']}
                          for r in j['workflow_runs'])
    return active


def form_fields(page,job):
    forms=re.findall(r'<form\b[^>]*id=["\']file_down["\'][^>]*>.*?</form>',page,re.S|re.I)
    if len(forms)!=1 or not re.search(r'action=["\']/get\.php["\']',forms[0],re.I):
        raise ValueError('declared free form not found; no substituted route')
    values={}
    for tag in re.findall(r'<input\b[^>]*>',forms[0],re.I):
        attrs=dict((k.lower(),html.unescape(v)) for k,_,v in
                   re.findall(r'(\w+)\s*=\s*(["\'])(.*?)\2',tag))
        if 'name' in attrs:values[attrs['name']]=attrs.get('value','')
    if any(values.get(k)!=v for k,v in job['post_fields'].items()) or not values.get('tk'):
        raise ValueError('free form asset/month/format differs from immutable plan')
    if set(values)!=set(job['post_fields'])|{'tk'}:
        raise ValueError('unexpected form field; do not submit')
    return values  # Public ephemeral tk is used locally, never printed/published.


def check_provider_checksums(headers,sha256,md5):
    headers={k.lower():v for k,v in headers.items()}
    proof={}
    if headers.get('content-md5'):
        if base64.b64decode(headers['content-md5'],validate=True).hex()!=md5:
            raise ValueError('provider MD5 mismatch')
        proof['content_md5_verified']=True
    advertised=[]
    if headers.get('x-checksum-sha256'):advertised.append(headers['x-checksum-sha256'].lower())
    for header in ('digest','content-digest'):
        for part in headers.get(header,'').split(','):
            if not part.strip():continue
            match=re.fullmatch(r'\s*(sha-256|md5)=:?([A-Za-z0-9+/=]+):?\s*',part,re.I)
            if not match:raise ValueError('unsupported advertised checksum; do not parse prices')
            algorithm=match[1].lower();value=base64.b64decode(match[2],validate=True).hex()
            if value!=(sha256 if algorithm=='sha-256' else md5):raise ValueError('provider digest mismatch')
            if algorithm=='sha-256':advertised.append(value)
            else:proof['digest_md5_verified']=True
    if any(value!=sha256 for value in advertised):raise ValueError('provider SHA256 mismatch')
    proof['provider_sha256']=sha256 if advertised else None
    return proof


def recover_file(root,job):
    root=Path(root);name=job['expected_archive_name'];final=root/name
    sidecar=root/(name+'.capture.json');part=root/(name+'.part')
    if not sidecar.exists():
        if final.exists():raise ValueError('unattributed completed archive; no overwrite or silent refresh')
        return None
    record=json.loads(sidecar.read_text())
    if record.get('name')!=name or record.get('page_url')!=job['page_url']:
        raise ValueError('persisted capture identity mismatch')
    candidate=final if final.exists() else part
    if candidate.is_symlink() or candidate.stat().st_size!=record['bytes'] or digest(candidate)!=record['sha256']:
        raise ValueError('saved capture bytes do not match original proof')
    if candidate==part:os.rename(part,final)
    return record


def capture_file(root,job):
    recovered=recover_file(root,job)
    if recovered:return recovered
    req=urllib.request.Request(job['page_url'],headers={'User-Agent':UA})
    with urllib.request.urlopen(req,timeout=30) as r:
        if 'text/html' not in r.headers.get('Content-Type',''):raise ValueError('page is not HTML')
        page=r.read(400001)
        if len(page)>400000:raise ValueError('bounded form metadata limit')
    values=form_fields(page.decode('utf-8'),job)
    time.sleep(1)  # At most one HistData request/s; never a long blocking wait.
    body=urllib.parse.urlencode(values).encode('ascii')
    req=urllib.request.Request(job['post_url'],data=body,headers={
        'User-Agent':UA,'Referer':job['page_url'],'Content-Type':'application/x-www-form-urlencoded'})
    name=job['expected_archive_name'];root=Path(root);part=root/(name+'.part')
    sha=hashlib.sha256();md5=hashlib.md5();size=0
    with urllib.request.urlopen(req,timeout=30) as r:
        if urllib.parse.urlsplit(r.geturl()).hostname not in ('histdata.com','www.histdata.com'):
            raise ValueError('unqualified redirected download source')
        headers=dict(r.headers.items())
        first=r.read(65536)
        if not first.startswith(b'PK\x03\x04'):raise ValueError('free form did not return a ZIP; do not bypass')
        with open(part,'wb') as f:
            block=first
            while block:
                f.write(block);sha.update(block);md5.update(block);size+=len(block)
                block=r.read(1024*1024)
            f.flush();os.fsync(f.fileno())
        if r.headers.get('Content-Length') and int(r.headers['Content-Length'])!=size:
            raise ValueError('incomplete compressed response')
    checksum=check_provider_checksums(headers,sha.hexdigest(),md5.hexdigest())
    record={'name':name,'page_url':job['page_url'],'post_url':job['post_url'],
        'form_metadata_sha256':hashlib.sha256(page).hexdigest(),
        'retrieved_utc':datetime.now(timezone.utc).isoformat(),
        'bytes':size,'sha256':sha.hexdigest(),'http_status':200,
        'provider_checksums':checksum,'price_rows_opened':0}
    # Durable proof precedes rename; an interrupted rename reuses the exact bytes.
    atomic_json(root/(name+'.capture.json'),record)
    os.rename(part,root/name)
    return record


def main():
    freeze=json.loads((HERE/'freeze.json').read_text());verify_freeze(HERE,freeze)
    manifest=json.loads((HERE/'manifest.json').read_text())
    if active_runs():raise RuntimeError('active run preserved; no capture started')
    CAPTURE.mkdir(parents=True,exist_ok=True)
    lock=CAPTURE/'capture.lock'
    if lock.exists():
        previous=json.loads(lock.read_text())
        if previous.get('host')!=socket.gethostname():raise RuntimeError('unreconciled capture lock')
        try:os.kill(previous['pid'],0)
        except ProcessLookupError:lock.unlink()
        else:raise RuntimeError('active capture preserved')
    atomic_json(lock,{'pid':os.getpid(),'host':socket.gethostname(),'manifest_sha256':digest(HERE/'manifest.json')})
    try:
        records=[]
        for job in manifest['archive_jobs']:
            # Preserve a run started after this capture; keep already-saved months.
            if active_runs(full=False):raise RuntimeError('new active run preserved; capture paused before next archive')
            records.append(capture_file(CAPTURE,job))
            time.sleep(1)
        certificate={'schema':1,'candidate':'EURUSD-RANGE-GRID-001',
            'status':'COMPLETE_NO_ROWS_OPENED','manifest_sha256':digest(HERE/'manifest.json'),
            'archives':records,'price_rows_opened':0}
        if (CAPTURE/'capture.json').exists():
            if json.loads((CAPTURE/'capture.json').read_text())!=certificate:
                raise ValueError('existing capture certificate mismatch')
        else:atomic_json(CAPTURE/'capture.json',certificate)
        print(json.dumps({'capture_status':certificate['status'],'archives':len(records),'price_rows_opened':0}))
    finally:lock.unlink()


if __name__=='__main__':main()
