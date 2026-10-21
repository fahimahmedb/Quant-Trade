"""Journal recovery uses newline as the durable record boundary."""

from concurrent.futures import ThreadPoolExecutor
import json

import pytest

from quant.state import append_jsonl, read_jsonl


@pytest.mark.parametrize("tail", [b'{"id":', b'{"id":2}', b'{"text":"\xe2',
                                  b'\xff', b'{"id":2}\r'])
def test_unterminated_tail_has_same_visibility_before_and_after_append(tmp_path, tail):
    path = tmp_path / "events.jsonl"
    path.write_bytes(b'{"id":1}\n' + tail)
    before = list(read_jsonl(path))
    assert before == [{"id": 1}]
    append_jsonl(path, {"id": 3})
    assert list(read_jsonl(path)) == before + [{"id": 3}]


@pytest.mark.parametrize("tail", [b'{"text":"\xe2', b'{"id":2}', b'\xff'])
def test_sec_never_discards_or_accepts_any_unterminated_tail(tmp_path, tail):
    path = tmp_path / "sec" / "evidence.jsonl"
    path.parent.mkdir()
    original = b'{"id":1}\n' + tail
    path.write_bytes(original)
    for action in (lambda: list(read_jsonl(path)), lambda: append_jsonl(path, {"id": 3})):
        with pytest.raises(ValueError, match="SEC_JOURNAL_TORN_TAIL"):
            action()
        assert path.read_bytes() == original


@pytest.mark.parametrize("record", [[], None, {"value": float("nan")}])
def test_rejected_append_cannot_repair_or_change_existing_bytes(tmp_path, record):
    path = tmp_path / "events.jsonl"
    original = b'{"id":1}\n{"partial":'
    path.write_bytes(original)
    with pytest.raises((ValueError, TypeError)):
        append_jsonl(path, record)
    assert path.read_bytes() == original


def test_unicode_committed_records_survive_a_torn_multibyte_append(tmp_path):
    path = tmp_path / "events.jsonl"
    committed = {"text": "日本語"}
    path.write_bytes((json.dumps(committed, ensure_ascii=False) + "\n").encode() + b'{"x":"\xe6\x97')
    assert list(read_jsonl(path)) == [committed]
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(lambda index: append_jsonl(path, {"index": index}), range(32)))
    records = list(read_jsonl(path))
    assert records[0] == committed
    assert sorted(record["index"] for record in records[1:]) == list(range(32))


def test_committed_invalid_utf8_is_loud(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_bytes(b'{"id":1}\n{"text":"\xff"}\n')
    with pytest.raises(UnicodeDecodeError):
        list(read_jsonl(path))
