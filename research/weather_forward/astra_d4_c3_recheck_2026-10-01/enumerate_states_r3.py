"""Exhaustive enumeration of spec @341e0b7a 17.1-17.6 (R3). No randomness."""
import itertools, json
VALID = ['INVALID_LEAKAGE', 'INVALID_PARAMETER_MUTATION', 'INVALID_REPLAY_MISMATCH', 'INVALID_DATA_FAILURE',
         'INVALID_DATA_COMPLETENESS', 'INVALID_MECHANICS_CHANGE_EARLY', 'VALID_TRUNCATED_MECHANICS_CHANGE', 'VALID_COMPLETE']
OPER = ['NOT_EVALUATED', 'INACCESSIBLE_LEGAL', 'NOT_OPERABLE_AS_TESTED', 'DEPTH_INSUFFICIENT', 'CAPITAL_INEFFICIENT', 'ACCESSIBLE']
FORBIDDEN = ('PROSPECTIVE', 'EXCLUDED', 'CONFIRMED_EDGE', 'DEPLOY', 'CAPITAL')
states, shadow_from, problems, n = set(), set(), [], 0
for v, info, T1, NEG, T2, thg, G, op in itertools.product(VALID, *[(0, 1)] * 6, OPER):
    n += 1
    if v.startswith('INVALID'): sci = 'NOT_EVALUATED'
    elif not info: sci = 'INFORMATION_INSUFFICIENT'
    else:
        ir = 'INFORMATION_DETECTED' if T1 else ('NEGATIVE_INFORMATION' if NEG else 'NO_INFORMATION_DETECTED')
        er = ('REALIZED_WINDOW_VALUE_SUPPORTED' if G else 'REALIZED_WINDOW_VALUE_NOT_ROBUST') if (T2 and thg) else 'REALIZED_WINDOW_VALUE_INDETERMINATE'
        sci = ir + '__' + er
    states.add(sci)
    shadow = v == 'VALID_COMPLETE' and sci.endswith('REALIZED_WINDOW_VALUE_SUPPORTED') and not NEG and op == 'ACCESSIBLE'
    cond_claim = sci.endswith('REALIZED_WINDOW_VALUE_SUPPORTED')     # CONDITIONAL_PROSPECTIVE_SUPPORT issued (17.3)
    constants = dict(PROSPECTIVE_EXCLUSION='NOT_USEFULLY_TESTABLE_IN_V2_HORIZON',
                     PROSPECTIVE_CONFIRMATION='NOT_ESTABLISHED_UNCONDITIONALLY', RSTAR='NOT_USEFULLY_TESTABLE_IN_V2_HORIZON')
    if shadow: shadow_from.add(sci)
    if any(f in sci for f in FORBIDDEN): problems.append(('forbidden_word_in_state', sci))
    if shadow and not cond_claim: problems.append(('shadow_without_supported', sci))
    if shadow and NEG: problems.append(('shadow_with_core_adverse', sci))
print(json.dumps(dict(combinations=n, scientific_values=len(states), values=sorted(states), shadow_only_from=sorted(shadow_from),
                      problems=problems, authorises=dict(builder=False, t0=False, capital=False, live=False))))
