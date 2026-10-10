"""Gated, write-once runner for the registered FX experiment; stdlib only.

No download, trade, fee/window override, selection or automatic retry. The
atomic GitHub ref must be created externally before this runner opens prices.
"""
from __future__ import annotations
import sys
sys.dont_write_bytecode=True

from datetime import timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile
import urllib.request
import zipfile

from safety_kernel import Quote, source_time_utc, envelope, CENTRAL, STRESS, sides
from engine import Engine, START, END, WARMUP_START, encode

HERE=Path(__file__).resolve().parent
CAPTURE=Path('/workspace/scratch/eurusd-range-grid-001/capture-v1')
OUTPUT=CAPTURE.parent/'result-exploratory-01'
REF='refs/heads/looks/eurusd-range-grid-001-exploratory-01'
REPO='fahimahmedb/Quant-Trade'
VERDICT_FIELDS=('RESULT','EFFECT_SIZE','UNCERTAINTY','POWER_LIMITATION',
    'ECONOMIC_SIGNIFICANCE','FAILED_CRITERIA','LESSON','FAMILY_STATUS','NEXT_DECISION')


class SourceError(ValueError):
    pass


def digest(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()


def atomic_json(path,value,*,exclusive=True):
    """No overwritten result or partially visible economic artifact."""
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    tmp=None;completed=False
    try:
        with tempfile.NamedTemporaryFile(mode='w',dir=path.parent,delete=False,
                prefix='result-' if path.name=='result.json' else 'metadata-',suffix='.tmp') as f:
            tmp=f.name
            json.dump(value,f,sort_keys=True,ensure_ascii=False,allow_nan=False)
            f.write('\n');f.flush();os.fsync(f.fileno())
        if exclusive:os.link(tmp,path)
        else:os.replace(tmp,path);tmp=None
        fd=os.open(path.parent,os.O_RDONLY)
        try:os.fsync(fd)
        finally:os.close(fd)
        completed=True
    finally:
        if tmp and (completed or path.name!='result.json'):os.unlink(tmp)


def verify_freeze(root,freeze):
    if freeze.get('schema')!=1 or not freeze.get('proxy_harness_frozen'):
        raise ValueError('harness gate open')
    if sys.version_info[:2]!=(3,12):raise ValueError('frozen Python minor mismatch')
    for name,expected in freeze['files'].items():
        if Path(name).name!=name or digest(Path(root)/name)!=expected:
            raise ValueError('published code/manifest identity mismatch')
    for name,expected in freeze['runtime_data'].items():
        if digest(name)!=expected:raise ValueError('timezone dependency identity mismatch')


def verify_claim(claim,freeze_sha,remote):
    if (claim.get('schema')!=1 or claim.get('ref')!=REF
            or claim.get('atomic_create_receipt') is not True
            or claim.get('freeze_sha256')!=freeze_sha
            or not re.fullmatch(r'[0-9a-f]{40}',claim.get('frozen_commit',''))
            or remote.get('ref')!=REF
            or remote.get('object',{}).get('sha')!=claim['frozen_commit']):
        raise ValueError('atomic reservation receipt does not match immutable remote ref')


def verify_capture(root,manifest,certificate):
    if (certificate.get('status')!='COMPLETE_NO_ROWS_OPENED'
            or certificate.get('manifest_sha256')!=digest(HERE/'manifest.json')
            or certificate.get('price_rows_opened')!=0):
        raise ValueError('capture certificate not complete/blind')
    jobs=manifest['archive_jobs'];records=certificate.get('archives',[])
    expected=[j['expected_archive_name'] for j in jobs]
    if [r.get('name') for r in records]!=expected or len(set(expected))!=len(expected):
        raise ValueError('capture does not exactly match declared months')
    for record in records:
        p=Path(root)/record['name']
        if p.is_symlink() or p.stat().st_size!=record['bytes'] or digest(p)!=record['sha256']:
            raise ValueError('immutable capture byte identity failure')
    return jobs


class ArchiveReader:
    """One ordered pass, strict month/schema and same-time adverse envelope."""
    def __init__(self,root,jobs):
        self.root=Path(root);self.jobs=jobs
        self.qa={'archives':[],'rows':0,'groups':0,'duplicates':0,
                 'multirow_groups':0,'outside_utc_rows_not_price_parsed':0}

    def groups(self):
        last_time=None;group=[];seen=set();current_time=None
        for job in self.jobs:
            month=job['source_local_month'].replace('-','')
            record={'month':month,'rows':0,'first_source_time':None,'last_source_time':None,
                    'first_utc':None,'last_utc':None}
            self.qa['archives'].append(record)
            try:
                with zipfile.ZipFile(self.root/job['expected_archive_name']) as z:
                    members=z.infolist()
                    csvs=[m for m in members if m.filename.lower().endswith('.csv')]
                    if (len(csvs)!=1 or not re.fullmatch(
                            '(?:DAT|HISTDATA_COM)_ASCII_EURUSD_T_'+month+r'\.csv',csvs[0].filename,re.I)
                            or csvs[0].flag_bits&1 or csvs[0].is_dir()):
                        raise SourceError('unexpected archive member/asset/month')
                    for m in members:
                        if Path(m.filename).name!=m.filename:raise SourceError('unexpected member path')
                    with z.open(csvs[0]) as f:
                        for index,raw in enumerate(f):
                            row=raw.rstrip(b'\r\n')
                            if index==0 and row==b'DateTime,Bid,Ask,Volume':continue
                            parts=row.split(b',')
                            if len(parts)!=4:raise SourceError('unexpected tick column count')
                            try:
                                source=parts[0].decode('ascii')
                                if source[:6]!=month:raise SourceError('timestamp outside declared source month')
                                utc=source_time_utc(source)
                            except (UnicodeError,ValueError) as e:
                                raise SourceError('unrecognized source timestamp') from e
                            time=int(utc.timestamp())*1000+utc.microsecond//1000
                            if last_time is not None and time<last_time:
                                raise SourceError('nonmonotone tick source; never sorted')
                            last_time=time;record['rows']+=1;self.qa['rows']+=1
                            if record['first_source_time'] is None:
                                record['first_source_time']=source;record['first_utc']=utc.isoformat()
                            record['last_source_time']=source;record['last_utc']=utc.isoformat()
                            if not WARMUP_START<=time<END:
                                self.qa['outside_utc_rows_not_price_parsed']+=1
                                continue
                            try:
                                q=Quote(time,float(parts[1]),float(parts[2]))
                                if not math.isfinite(q.mid):raise ValueError('invalid mid')
                                if any(sides(q,c)[0]<=0 or not math.isfinite(sides(q,c)[1]) for c in (CENTRAL,STRESS)):
                                    raise ValueError('invalid cost envelope')
                            except (ValueError,OverflowError) as e:
                                raise SourceError('invalid positive finite bid/ask/cost envelope') from e
                            if current_time is not None and time!=current_time:
                                self.qa['groups']+=1
                                if len(group)>1:self.qa['multirow_groups']+=1
                                yield envelope(group)
                                group=[];seen=set()
                            if row in seen:self.qa['duplicates']+=1
                            seen.add(row);group.append(q);current_time=time
                    # Metadata members are CRC checked too, never interpreted as prices.
                    for m in members:
                        if m is csvs[0]:continue
                        with z.open(m) as f:
                            for block in iter(lambda:f.read(1024*1024),b''):pass
                if record['rows']==0:raise SourceError('empty declared month')
            except (zipfile.BadZipFile,EOFError,UnicodeError) as e:
                raise SourceError('archive/CRC/schema failure') from e
        if group:
            self.qa['groups']+=1
            if len(group)>1:self.qa['multirow_groups']+=1
            yield envelope(group)


def begin_attempt(output,claim,resume_certificate=None):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    if (output/'result.json').exists() or list(output.glob('result*.tmp')):
        raise FileExistsError('prior/partial result present; preserve, never recalculate')
    attempt=output/'attempt.json'
    if attempt.exists():
        previous=json.loads(attempt.read_text())
        if resume_certificate is None:raise FileExistsError('reserved attempt exists; explicit published no-outcome proof required')
        cert=resume_certificate
        if (previous.get('state')!='INFRASTRUCTURE_FAILURE_NO_RESULT'
                or cert.get('previous_attempt_sha256')!=digest(attempt)
                or cert.get('no_printed_or_saved_outcome') is not True
                or cert.get('all_artifact_log_local_public_stores_checked') is not True
                or cert.get('ref')!=REF or cert.get('frozen_commit')!=claim['frozen_commit']
                or not re.fullmatch(r'https://github.com/fahimahmedb/Quant-Trade/pull/22#issuecomment-\d+',cert.get('public_review_url',''))):
            raise ValueError('resume lacks exact no-outcome/reservation proof')
        atomic_json(output/'resume-proof.json',cert)
    value={'schema':1,'ref':REF,'frozen_commit':claim['frozen_commit'],
           'state':'RUNNING_NO_RESULT_PRINTED','result_written':False}
    atomic_json(attempt,value,exclusive=not attempt.exists())
    return value


def failure_result(engine,reason,reader_qa):
    r=engine.result()
    r['verdict']['RESULT']='SOURCE_GATE_FAILED'
    r['verdict']['FAILED_CRITERIA']['source_failure']=reason
    r['verdict']['NEXT_DECISION']='Park this exact source/proxy with failure and partial/residual evidence; no automatic repeat, tuning or economic rejection.'
    r['reader_qa']=reader_qa
    r['partial_exposure']=encode(engine)
    r['partial_marked_equity']={p.expression+('_CENTRAL' if p.costs==CENTRAL else '_STRESS'):
        {'liquidation_side_nav':p.nav(engine.last) if engine.last else p.cash,
         'adverse_unresolved_stop_nav':p.nav(engine.last,unresolved=True) if engine.last else p.cash,
         'open_units':p.basket.units if p.basket else 0} for p in engine.paths}
    return r


def validate_result(result,schema):
    if (result.get('schema')!=schema['schema'] or result.get('candidate')!=schema['candidate']
            or not set(schema['required_top_level'])<=set(result)
            or set(result.get('verdict',{}))!=set(schema['verdict_fields'])
            or set(result.get('paths',{}))!=set(schema['path_keys'])
            or set(result.get('paired_central',{}))!=set(schema['paired_central_keys'])
            or not result['verdict']['RESULT']
            or not set(result['verdict']['RESULT'].split(';'))<=set(schema['allowed_results'])):
        raise ValueError('frozen six-path/nine-field result schema failure')


def main():
    freeze=json.loads((HERE/'freeze.json').read_text())
    verify_freeze(HERE,freeze)
    manifest=json.loads((HERE/'manifest.json').read_text())
    certificate=json.loads((CAPTURE/'capture.json').read_text())
    jobs=verify_capture(CAPTURE,manifest,certificate)
    claim=json.loads((CAPTURE/'reservation.json').read_text())
    url='https://api.github.com/repos/'+REPO+'/git/ref/heads/looks/eurusd-range-grid-001-exploratory-01'
    req=urllib.request.Request(url,headers={'User-Agent':'quant-research-personal-backtest/0.1'})
    with urllib.request.urlopen(req,timeout=30) as response:remote=json.load(response)
    verify_claim(claim,digest(HERE/'freeze.json'),remote)
    # CLI GH auth is unnecessary; creation/receipt uses the available connector.
    if len(sys.argv)>2:raise ValueError('no strategy/window/cost/output overrides')
    resume=json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv)==2 else None
    attempt=begin_attempt(OUTPUT,claim,resume)
    e=Engine();reader=ArchiveReader(CAPTURE,jobs)
    def persist_warmup(state):
        warmup=OUTPUT/'warmup-state.json'
        if warmup.exists():
            if json.loads(warmup.read_text())!=state:raise SourceError('saved calibration identity mismatch')
        else:atomic_json(warmup,state)
    try:
        for q in reader.groups():
            if any(p.basket and not math.isfinite(p.basket.units*q.mid) for p in e.paths):
                raise SourceError('unrepresentable marked notional')
            e.feed(q,warmup_sink=persist_warmup)
        result=e.finalize();result['reader_qa']=reader.qa
    except (SourceError,ValueError,ArithmeticError) as error:
        # No traceback/value preview: source failure itself consumes exposure.
        result=failure_result(e,type(error).__name__+':'+str(error),reader.qa)
    except (OSError,TimeoutError):
        attempt['state']='INFRASTRUCTURE_FAILURE_NO_RESULT'
        atomic_json(OUTPUT/'attempt.json',attempt,exclusive=False)
        raise RuntimeError('infrastructure interrupted; no economic result printed; proof required before any resume') from None
    # No early P&L/count/Sharpe print. Revalidate immutable code and capture bytes.
    verify_freeze(HERE,freeze);verify_capture(CAPTURE,manifest,certificate)
    result['integrity']={'frozen_commit':claim['frozen_commit'],'freeze_sha256':digest(HERE/'freeze.json'),
        'manifest_sha256':digest(HERE/'manifest.json'),'capture_sha256':digest(CAPTURE/'capture.json'),
        'reservation_ref':REF,'raw':certificate['archives']}
    validate_result(result,json.loads((HERE/'result_schema.json').read_text()))
    atomic_json(OUTPUT/'result.json',result)
    attempt.update(state='RESULT_SAVED_LOOK_CONSUMED',result_written=True,
                   result_sha256=digest(OUTPUT/'result.json'))
    atomic_json(OUTPUT/'attempt.json',attempt,exclusive=False)
    print(json.dumps({'result_sha256':attempt['result_sha256'],'verdict':result['verdict']},ensure_ascii=False,allow_nan=False))


if __name__=='__main__':main()
