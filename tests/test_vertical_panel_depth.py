import pytest

from quant.dataplane.panel import PricePanel
from quant.dataplane.validation import validate_panel


def rows():
    return [{'date': f'2026-01-{i:02d}', 'symbol': symbol,
             'open': 100+i, 'high': 100+i, 'low': 100+i, 'close': 100+i,
             'adj_close': 100+i, 'volume': 1000} for i in range(1, 11) for symbol in ['A', 'B']]


@pytest.mark.parametrize('method', ['aligned_dates','dates_for'])
def test_date_view_mutation_cannot_corrupt_future_alignment(method):
    panel = PricePanel(rows())
    get = (lambda: panel.aligned_dates(['A','B'])) if method == 'aligned_dates' else (lambda: panel.dates_for('A'))
    original = get().copy()
    get().reverse()
    assert get() == original
    get().clear()
    assert get() == original
    assert panel.aligned_index(['A','B'], original[0]) == 0


@pytest.mark.parametrize('view', ['restrict', 'window'])
def test_duplicate_evidence_survives_same_panel_projection(view):
    from quant.dataplane.panel import Window
    data = rows()
    panel = PricePanel(data + [data[0]])
    projected = panel.restrict() if view == 'restrict' else panel.window(Window('selected','2026-01-01','2026-01-10'))
    assert projected.duplicate_keys == panel.duplicate_keys
    assert validate_panel(projected, ['A','B'], min_rows_per_symbol=1)['passed'] is False


def test_projection_excluding_duplicate_key_can_be_clean():
    data = rows()
    panel = PricePanel(data + [data[0]])
    projected = panel.restrict(start='2026-01-02')
    assert projected.duplicate_keys == []
    assert validate_panel(projected, ['A','B'], min_rows_per_symbol=1)['passed']


def test_export_cannot_silently_erase_duplicate_evidence(tmp_path):
    data = rows()
    panel = PricePanel(data + [data[0]])
    path = tmp_path / 'panel.csv'
    path.write_text('old file')
    with pytest.raises(ValueError, match='duplicate'):
        panel.write(path)
    assert path.read_text() == 'old file'


@pytest.mark.parametrize('fractions', [{'a':-0.1,'b':1.1}, {'a':0,'b':1}, {'a':True},
    {'a':float('nan'),'b':float('nan')}, {'a':float('inf'),'b':-float('inf')}, {'a':.4,'b':.4}])
def test_invalid_split_fractions_are_rejected(fractions):
    with pytest.raises(ValueError):
        PricePanel(rows()).split(fractions)


def test_valid_splits_cover_each_session_exactly_once():
    panel = PricePanel(rows())
    windows = panel.split({'research':.6,'validation':.3,'reserved':.1}, ['A','B'])
    memberships = [[d for d in panel.dates if w.contains(d)] for w in windows.values()]
    assert [d for group in memberships for d in group] == panel.dates
    assert all(memberships)
    assert len({d for group in memberships for d in group}) == len(panel.dates)
