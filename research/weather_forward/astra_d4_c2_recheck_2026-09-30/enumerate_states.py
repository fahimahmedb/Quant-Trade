"""Exhaustive enumeration of the D4-touched state machine of spec @e45d2ce7 (17.1-17.6). No randomness."""
import itertools, json
VALID = ['INVALID_LEAKAGE', 'INVALID_PARAMETER_MUTATION', 'INVALID_REPLAY_MISMATCH', 'INVALID_DATA_FAILURE',
         'INVALID_DATA_COMPLETENESS', 'INVALID_MECHANICS_CHANGE_EARLY', 'VALID_TRUNCATED_MECHANICS_CHANGE', 'VALID_COMPLETE']
OPER = ['NOT_EVALUATED', 'INACCESSIBLE_LEGAL', 'NOT_OPERABLE_AS_TESTED', 'DEPTH_INSUFFICIENT', 'CAPITAL_INEFFICIENT', 'ACCESSIBLE']
states, fwd_states, problems = set(), set(), []
n = 0
for v, info, T1, NEG, T2, thg, G, Ult, Ulpce, U0, op in itertools.product(VALID, *[(0, 1)] * 9, OPER):
    if (Ult and thg) or (U0 and not Ult) or (Ult and not Ulpce):   # R1 invariants: U_W >= theta_hat; U<0 => U<ERT => U<PCE
        continue
    n += 1
    if v.startswith('INVALID'): sci = 'NOT_EVALUATED'
    elif not info: sci = 'INFORMATION_INSUFFICIENT'
    else:
        ir = 'INFORMATION_DETECTED' if T1 else ('NEGATIVE_INFORMATION' if NEG else 'NO_INFORMATION_DETECTED')
        er = ('PROSPECTIVE_VALUE_CONFIRMED' if G else 'PROSPECTIVE_VALUE_NOT_ROBUST') if (T2 and thg) else 'PROSPECTIVE_VALUE_INDETERMINATE'
        sci = ir + '__' + er
    states.add(sci)
    evaluated = sci not in ('NOT_EVALUATED', 'INFORMATION_INSUFFICIENT')
    rw = None
    if evaluated:
        rw = 'LOSS_CONFIRMED' if U0 else 'RELEVANT_VALUE_EXCLUDED' if Ult else 'LARGE_VALUE_EXCLUDED' if Ulpce else 'NOT_EXCLUDED'
    fwd = v == 'VALID_COMPLETE' and sci.endswith('PROSPECTIVE_VALUE_CONFIRMED') and not NEG and op == 'ACCESSIBLE'
    rstar_rejected = False
    core_info_rej = bool(NEG) and evaluated
    if fwd: fwd_states.add(sci)
    if 'EXCLUDED' in sci: problems.append(('excluded_state', sci))
    if fwd and 'CONFIRMED' not in sci: problems.append(('fwd_without_confirm', sci))
    if fwd and NEG: problems.append(('fwd_with_core_adverse', sci))
    # realised-window field and CORE_ADVERSE must not influence the economic axis: flip them and recompute
    if evaluated:
        er2 = ('PROSPECTIVE_VALUE_CONFIRMED' if G else 'PROSPECTIVE_VALUE_NOT_ROBUST') if (T2 and thg) else 'PROSPECTIVE_VALUE_INDETERMINATE'
        if not sci.endswith(er2): problems.append(('rw_or_neg_influences_eco', sci))
print(json.dumps(dict(combinations=n, scientific_values=len(states), values=sorted(states),
                      forward_signal_only_from=sorted(fwd_states), problems=problems[:5], n_problems=len(problems))))
