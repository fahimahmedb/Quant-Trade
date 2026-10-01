"""ASTRA D4-C3-M1 recheck: enumerate the SCIENTIFIC_STATE partition and derived fields from spec 17.1-17.6 at 4423c5c3,
written from the spec text (independent of earlier enumerators). Deterministic, no randomness."""
import itertools
import json

VALIDITY = ['INVALID_LEAKAGE', 'INVALID_PARAMETER_MUTATION', 'INVALID_REPLAY_MISMATCH', 'INVALID_DATA_FAILURE',
            'INVALID_DATA_COMPLETENESS', 'INVALID_MECHANICS_CHANGE_EARLY', 'VALID_TRUNCATED_MECHANICS_CHANGE', 'VALID_COMPLETE']
OPER = ['NOT_EVALUATED', 'INACCESSIBLE_LEGAL', 'NOT_OPERABLE_AS_TESTED', 'DEPTH_INSUFFICIENT', 'CAPITAL_INEFFICIENT', 'ACCESSIBLE']


def scientific(v, info, T1a, T1b, NEG, T2, ert, gates):
    if v.startswith('INVALID'):
        return 'NOT_EVALUATED'
    if not info:
        return 'INFORMATION_INSUFFICIENT'
    T1 = T1a or T1b
    ir = 'INFORMATION_DETECTED' if T1 else ('NEGATIVE_INFORMATION' if NEG else 'NO_INFORMATION_DETECTED')
    if T2 and ert and gates:
        er = 'REALIZED_WINDOW_VALUE_SUPPORTED'
    elif T2 and ert:
        er = 'REALIZED_WINDOW_VALUE_NOT_ROBUST'
    else:
        er = 'REALIZED_WINDOW_VALUE_INDETERMINATE'
    return ir + '__' + er


states = set()
shadow_from = set()
core_rej = 0
combos = 0
neg_and_t1a = 0
for v, info, T1a, T1b, NEG, T2, ert, gates, op in itertools.product(VALIDITY, *[[False, True]] * 7, OPER):
    if T1a and NEG:      # kappa_hat - t SE > 0 and kappa_hat + t SE < 0 cannot both hold (SE >= 0)
        neg_and_t1a += 1
        continue
    combos += 1
    s = scientific(v, info, T1a, T1b, NEG, T2, ert, gates)
    states.add(s)
    evaluated = s not in ('NOT_EVALUATED', 'INFORMATION_INSUFFICIENT')
    core_adverse = bool(NEG) if evaluated else None
    shadow = (v == 'VALID_COMPLETE' and s.endswith('REALIZED_WINDOW_VALUE_SUPPORTED') and core_adverse is False
              and op == 'ACCESSIBLE')
    if shadow:
        shadow_from.add(s)
    core_rej += bool(evaluated and NEG)
bad_words = [s for s in states if any(w in s for w in ('PROSPECTIVE', 'EXCLUDED', 'DEPLOY', 'CAPITAL', 'EDGE', 'CONFIRMED'))]
print(json.dumps(dict(combinations=combos, impossible_T1a_and_NEG_skipped=neg_and_t1a, n_states=len(states),
                      states=sorted(states), shadow_signal_only_from=sorted(shadow_from), forbidden_words_in_states=bad_words,
                      R_star_rejected_as_net_strategy_reachable=False,
                      note='R*_REJECTED_AS_NET_STRATEGY has no condition in 17.6 (never issued); CORE_ADVERSE = NEG'), indent=1))
