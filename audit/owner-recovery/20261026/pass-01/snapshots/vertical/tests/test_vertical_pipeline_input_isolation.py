from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import threading

import pytest

from research.research_os.expansion import v2_pipeline as pipeline


@pytest.mark.parametrize('mutation',['negative_list','negative_tuple','export_identity'])
def test_preoutcome_scan_and_final_receipt_use_one_detached_bundle(monkeypatch,mutation):
    supplied=json.loads(Path('tests/fixtures/oracle_v2_core_fixture.json').read_text())
    original=deepcopy(supplied)
    expected=pipeline.run_pre_outcome_pipeline(original)
    entered,release=threading.Event(),threading.Event();priority=pipeline.build_priority_decision
    def paused(**kwargs):
        result=priority(**kwargs)
        entered.set();assert release.wait(5)
        return result
    monkeypatch.setattr(pipeline,'build_priority_decision',paused)
    with ThreadPoolExecutor(max_workers=1) as pool:
        future=pool.submit(pipeline.run_pre_outcome_pipeline,supplied)
        try:
            assert entered.wait(5)
            if mutation=='export_identity':supplied['export']['research_head']='a'*40
            else:
                hidden={'returns':'SYNTHETIC_FORBIDDEN_CONTENT'}
                supplied['negative_memory']['untrusted_extension']=[hidden] if mutation=='negative_list' else (hidden,)
        finally:release.set()
        observed=future.result()
    assert observed==expected
    assert observed['negative_knowledge_hash']==expected['negative_knowledge_hash']
    assert observed['outcome_accessed'] is False
    assert all(value is False for value in observed['authority'].values())
