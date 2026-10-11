"""Distinct noon-to-evening physical proxy, using the pinned SMARD reader.

Not a retry or computation of the spent 03-to-18 protocol. Solar generation's
daylight timing motivates the noon input before any prices are inspected.
"""
import json
import statistics
from datetime import datetime, timedelta

from .smard import BERLIN, WINDOW, SourceError, capture, parse, mean_interval
from .store import digest

DESIGN = {"charge_local_hour":12,"discharge_local_hour":18,"input_mwh":1,
          "round_trip_efficiency":0.8,"central_all_in_eur":100,"stress_all_in_eur":150}


def calculate(quotes):
    gross = []
    day = datetime(2025,1,1)
    while day.year == 2025:
        buy = int(day.replace(hour=12,tzinfo=BERLIN).timestamp()*1000)
        sell = int(day.replace(hour=18,tzinfo=BERLIN).timestamp()*1000)
        gross.append(0.8*quotes[sell]-quotes[buy])
        day += timedelta(days=1)
    paths = {}
    for name,cost in (("central",100.0),("stress",150.0)):
        values = [v-cost for v in gross]
        cumulative = peak = drawdown = 0.0
        for v in values:
            cumulative += v
            peak=max(peak,cumulative)
            drawdown=min(drawdown,cumulative-peak)
        paths[name] = {"all_in_assumed_eur_per_input_mwh":cost,
            "mean_net_eur_per_input_mwh":statistics.fmean(values),"annual_net_eur_per_1mwh_device":sum(values),
            "daily_mean_hac7_95pct_interval":mean_interval(values),"worst_day_eur":min(values),
            "negative_days":sum(v<0 for v in values),"max_daily_cash_pnl_drawdown_eur":drawdown}
    kind=("NEGATIVE" if paths['central']['daily_mean_hac7_95pct_interval'][1]<0 else
          "POSITIVE_EXPLORATORY" if paths['stress']['daily_mean_hac7_95pct_interval'][0]>0 else "INSUFFICIENT_POWER")
    return kind,paths,{"mean_gross_break_even_all_in_cost_eur_per_input_mwh":statistics.fmean(gross),
        "gross_mean_hac7_95pct_interval":mean_interval(gross)}


def run(root,protocol_id,look_id):
    s=json.loads((root/'research/edge_lab/STATE.json').read_text())
    p,look=s['protocols'][protocol_id],s['looks'][look_id]
    if look['status']!='RUNNING_SPENT' or p['window']!=WINDOW or p['design']!=DESIGN:
        raise ValueError('Exact noon schedule and RUNNING reservation required')
    manifest=json.loads((root/p['input_manifest']).read_text())
    if digest(manifest)!=look['data_fingerprint']:
        raise ValueError('Source version differs from reservation')
    directory=root/'research/edge_lab/receipts'/digest(look_id)
    observations={"scheduled_days":365,"days_computed":0,"market_units":"delivery-hour outcomes; calendar-day cash-PnL units"}
    paths={c:{"net":None,"reason":"capture/whole-window QA incomplete"} for c in p['cost_paths']}
    effect={"estimated":False,"reason":"source not acquired"}
    failed=["Physical asset, original executable orders/grid tariffs/failed dispatch not established; proxy only",
            "One-year historical sample, private exposure/effective trials UNKNOWN; no independent confirmation"]
    try:
        records,hashes=capture(manifest,directory)
        q,qa=parse(records)
        kind,paths,gross=calculate(q)
        observations.update(days_computed=365,source_qa=qa,input_files=hashes)
        effect={**gross,"net_mean_eur_per_input_mwh":{c:x['mean_net_eur_per_input_mwh'] for c,x in paths.items()}}
        nature='EXPLORATORY_BACKTEST'
        if kind=='NEGATIVE':failed.append('Central full-cost daily-mean95pct upper bound below0')
        elif kind=='INSUFFICIENT_POWER':failed.append('Stress full-cost lower bound not strictly positive; uncertainty/cost-model qualification required')
    except (SourceError,KeyError,ValueError,OSError,TimeoutError) as exc:
        kind,nature='SOURCE_UNUSABLE','SOURCE_FAILURE'
        failed.append(type(exc).__name__+': '+str(exc)[:180])
    status={'NEGATIVE':'REJECTED_EXACT_NOON_POLICY_AT_ASSUMED_COSTS','POSITIVE_EXPLORATORY':'VALIDATION_REQUIRED_PROXY_ONLY',
            'INSUFFICIENT_POWER':'INCONCLUSIVE_WAIT','SOURCE_UNUSABLE':'BLOCKED_DATA_ACCESS'}[kind]
    lesson=('Preserve one fixed solar-timing expression, efficiency loss, both full assumed costs and gross break-even cost. '
            'Rejecting this policy does not reject storage, solar flexibility or a market. Never replace hours/costs with a winner.')
    next_action=('Close this exact noon-to-evening100EUR-cost policy; retain gross break-even cost without authorizing a cheaper-cost rerun.'
                 if kind=='NEGATIVE' else 'Wait for distinct source/physical execution/tariff evidence; no automatic rerun, retuning or capital use.')
    uncertainty={'method':'Descriptive95pct daily-mean Newey-West/Bartlett HAC lag7 fixed before prices',
        'intervals':{c:x.get('daily_mean_hac7_95pct_interval') for c,x in paths.items()},
        'limits':'365days not365independent experiments; one year, tails/regimes/revisions/seasonality/private historyUNKNOWN. Normal approximation not guaranteed coverage.'}
    verdict={'RESULT':kind,'EFFECT_SIZE':effect,'UNCERTAINTY':uncertainty,
        'POWER_LIMITATION':'365scheduled days,serial dependence,one year; previous no-price software look2paths + this policy2paths; effectiveM UNKNOWN',
        'ECONOMIC_SIGNIFICANCE':'EUR/inputMWh after assumed100/150EUR complete costs and20pct energy loss; neither real tariff quote nor executable financial alpha',
        'FAILED_CRITERIA':failed,'LESSON':lesson,'FAMILY_STATUS':status,'NEXT_DECISION':next_action}
    return {'look_id':look_id,'kind':kind,'nature':nature,'protocol_hash':p['hash'],'data_fingerprint':look['data_fingerprint'],
        'primary':p['primary'],'benchmark':'No device/no order incremental cashPnl0','observations':observations,
        'net_after_costs':paths,'expression_results':{p['primary']:paths},'uncertainty':uncertainty,
        'risk_exposures':{'inventory':'1MWh input,0.8MWh output,one6h cycle/day','credit':'Counterparty/market membership and collateral not established',
                          'limits':'Failed physical dispatch/imbalance/real grid fees not priced from authentic contracts; all-in cost paths explicitly assumed'},
        'capacity':'1MW input/1MWh physical proxy only, no purchased plant/market impact/scaling/live entitlement',
        'lesson':lesson,'next_decision':next_action,'verdict':verdict,'attribution':'Bundesnetzagentur | SMARD.de, CC BY4.0'}
