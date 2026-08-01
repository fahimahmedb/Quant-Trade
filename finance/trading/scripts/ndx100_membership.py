"""Composition POINT-IN-TIME du NASDAQ-100 (2015-2026) — portage minimal
et fidèle du paquet `nasdaq-100-ticker-history` v2026.7.0
(https://github.com/jmccarrell/n100tickers, licence MIT, auteur Jeff
McCarrell), vendoré au cycle #163 du backlog non-ML.

Pourquoi un portage plutôt qu'un `pip install` : l'environnement de ce
projet n'autorise pas l'installation de paquets, et le paquet amont
dépend de `strictyaml` (également indisponible). Les DONNÉES (les 12
fichiers `n100-ticker-changes-YYYY.yaml`) sont copiées **verbatim, sans
aucune modification**, dans `data/ndx100_history/` ; seule la fonction de
chargement est réécrite avec PyYAML (déjà présent). La logique de
`tickers_as_of` ci-dessous est une transcription littérale de
`src/nasdaq_100_ticker_history/n100tickers.py` amont (union/difference
appliquées dans l'ordre chronologique des dates de changement <= date
demandée) — vérifiée par `test_matches_upstream_doctest()`.

Couverture documentée par l'amont : 2015-01-01 → au moins 2026-06-22.
Hors de cette fenêtre, aucune donnée point-in-time n'existe ici.
"""
import datetime
import functools
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "ndx100_history"
FIRST_YEAR, LAST_YEAR = 2015, 2026
UPSTREAM_VERSION = "2026.7.0"
UPSTREAM_URL = "https://github.com/jmccarrell/n100tickers"


class _TickerLoader(yaml.SafeLoader):
    """PyYAML applique la résolution booléenne YAML 1.1 : le ticker `ON` (ON
    Semiconductor, membre du NDX-100 de 2022 à 2024) serait chargé comme
    `True`, de même que d'éventuels `NO`/`Y`/`N`/`OFF`. Le paquet amont
    utilise `strictyaml`, qui n'a PAS ce comportement (tout est `Str()` dans
    son schéma). On désactive donc explicitement le résolveur booléen pour
    rester fidèle à l'amont. Bug détecté et corrigé AVANT tout calcul."""


_TickerLoader.yaml_implicit_resolvers = {
    k: [(tag, regexp) for tag, regexp in v if tag != "tag:yaml.org,2002:bool"]
    for k, v in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


@functools.lru_cache(maxsize=None)
def _load_year(year: int) -> dict:
    path = DATA_DIR / f"n100-ticker-changes-{year}.yaml"
    if not path.is_file():
        raise NotImplementedError(f"aucune composition NDX-100 disponible pour {year} ({path})")
    return yaml.load(path.read_text(encoding="utf-8"), Loader=_TickerLoader)


def tickers_as_of(year: int, month: int = 1, day: int = 1) -> frozenset:
    """Ensemble exact des tickers membres du NDX-100 à cette date."""
    y = _load_year(year)
    result = set(y["tickers_on_Jan_1"])
    changes = y.get("changes") or {}
    query = datetime.date(year, month, day)
    for key in sorted(changes.keys()):
        d = datetime.date.fromisoformat(str(key))
        if d <= query:
            for operation, operands in changes[key].items():
                if operation == "union":
                    result |= set(operands)
                elif operation == "difference":
                    result -= set(operands)
                else:
                    raise NotImplementedError(f"opération inconnue : {operation} ({key})")
    return frozenset(result)


def tickers_as_of_date(d) -> frozenset:
    """Idem, à partir d'un objet date/Timestamp."""
    return tickers_as_of(d.year, d.month, d.day)


def all_tickers_ever(first_year: int = FIRST_YEAR, last_year: int = LAST_YEAR) -> frozenset:
    """Union de TOUS les tickers ayant appartenu à l'indice sur la fenêtre —
    c'est l'univers de prix qu'il faut avoir récupéré pour éliminer le
    biais du survivant (et non la seule liste des membres actuels)."""
    ever = set()
    for year in range(first_year, last_year + 1):
        y = _load_year(year)
        ever |= set(y["tickers_on_Jan_1"])
        for ops in (y.get("changes") or {}).values():
            for operands in ops.values():
                ever |= set(operands)
    return frozenset(ever)


def test_matches_upstream_doctest() -> None:
    """Reproduit les doctests publiés en amont (n100tickers.py) — garantit
    que le portage n'a pas divergé de la sémantique originale."""
    assert "TSLA" in tickers_as_of(2020, 9, 1)
    assert len(tickers_as_of(2020, 9, 1)) == 103, len(tickers_as_of(2020, 9, 1))
    # garde-fou anti-résolution booléenne (cf. _TickerLoader)
    assert "ON" in tickers_as_of(2024, 1, 1), "ticker ON perdu par la résolution YAML 1.1"
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        assert all(isinstance(t, str) for t in tickers_as_of(year, 12, 31))


if __name__ == "__main__":
    test_matches_upstream_doctest()
    ever = all_tickers_ever()
    print(f"Portage OK (doctests amont reproduits). Tickers ayant appartenu au "
          f"NDX-100 entre {FIRST_YEAR} et {LAST_YEAR} : {len(ever)}")
    for y in range(FIRST_YEAR, LAST_YEAR + 1):
        print(f"  {y}-01-01 : {len(tickers_as_of(y, 1, 1))} membres")
