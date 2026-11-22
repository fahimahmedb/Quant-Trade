#!/usr/bin/env python3
"""Quant-Trade — ECONOMIC MECHANISM TESTS, 2026-11-22.
No price data, orders, capital, new strategy or historical backtest.
Published-source numeric data are distinct from explicit synthetic assumptions.
Existing canonical GitHub experiments are independently checked only at RESULT/IDENTITY LEVEL.
"""
import json, math, hashlib, pathlib, statistics
from scipy.optimize import brentq

ROOT=pathlib.Path('/mnt/data')
checks=[]

def ck(cond, label):
    if not cond: raise AssertionError(label)
    checks.append(label)

def eq(a,b,label,tol=1e-9): ck(math.isclose(a,b,rel_tol=tol,abs_tol=tol),label)

# 01 / H-DRYPOWDER. Purely hypothetical cash reserve vs invest now.
def drypowder(cash=.03,equity=.07,T=5,t=3,p=.25,d=.1,friction=0,permanent_haircut=0,reserve_fraction=1):
    """Return as fraction of market-only terminal wealth; fixed market compound base.
    At event: cash from 0..t, buy at discount, assume immediate return to fraction (1-haircut)
    of notional 'fair value', reinvest until T; if no event cash remains to T."""
    q=(1+cash)/(1+equity)
    event=q**t*(1-permanent_haircut)*(1-friction)/(1-d)
    none=q**T
    rel_event=1+reserve_fraction*(event-1)
    rel_none=1+reserve_fraction*(none-1)
    return dict(event=rel_event,nonevent=rel_none,expected=p*rel_event+(1-p)*rel_none,
                event_prob=p,discount=d,friction=friction,haircut=permanent_haircut,reserve_fraction=reserve_fraction)

def critical_discount(cash=.03,equity=.07,T=5,t=3,p=.25,friction=0,permanent_haircut=0):
    if p==0: return None
    q=(1+cash)/(1+equity)
    denom=1-(1-p)*q**T
    if denom<=0: return None
    return 1-p*q**t*(1-permanent_haircut)*(1-friction)/denom

D0=drypowder(); dcrit=critical_discount();dcert=critical_discount(p=1)
eq(dcrit,0.41330326448193455,'D01 prob=25% hurdle')
eq(dcert,1-(1.03/1.07)**3,'D02 certain event hurdle')
eq(drypowder(d=dcrit)['expected'],1,'D03 threshold indifference')
ck(drypowder(d=.1)['expected']<1,'D04 10pct discount does not imply outperformance')
ck(drypowder(d=.2)['expected']>drypowder(d=.1)['expected'],'D05 larger discount increases synthetic proceeds')
ck(drypowder(p=.5,d=.2)['expected']>drypowder(p=.25,d=.2)['expected'],'D06 more events help in this optimistic case')
ck(drypowder(d=.2,friction=.01)['expected']<drypowder(d=.2)['expected'],'D07 fees damage case')
ck(drypowder(d=.2,permanent_haircut=.05)['expected']<drypowder(d=.2)['expected'],'D08 nonrecovering marked discount damages case')
eq(drypowder(d=.2,reserve_fraction=0)['expected'],1,'D09 zero reserve equals baseline')
eq((drypowder(d=.2,reserve_fraction=.25)['expected']-1)*4,drypowder(d=.2,reserve_fraction=1)['expected']-1,'D10 linear capital fraction within hypothetical model')
# Explicit stress grid, not a search for fit, no statistical tests.
dry_grid=[{**{'p':p,'d':d},'relative_terminal_delta':drypowder(p=p,d=d)['expected']-1}
          for p in (0,.25,.5,1) for d in (.1,.2,.3,.4)]

# 02 / H-ILS — primary published 2024/2026 World Bank amounts and modeled ELs.
cat={'2024':{'notional_musd':150,'margin':.07,'EL':.0161,'attach':.0246,'exhaust':.0084},
     '2026':{'notional_musd':200,'margin':.0675,'EL':.0248,'attach':.0386,'exhaust':.0108}}
for year, b in cat.items():
    b['annual_margin_musd']=b['notional_musd']*b['margin']
    b['annual_model_EL_musd']=b['notional_musd']*b['EL']
    b['gross_margin_minus_model_EL_pp']=100*(b['margin']-b['EL'])
    b['EL_over_margin']=b['EL']/b['margin']
    b['stress']=[{'EL_multiplier':m,'annual_frictions_rate':.01,
                  'margin_minus_stressed_EL_and_cost_pp':100*(b['margin']-m*b['EL']-.01)}
                 for m in (1,2,3)]
    ck(0<b['exhaust']<=b['attach'],'C01_'+year+' trigger ordering')
    ck(b['margin']>b['EL'],'C02_'+year+' margin over model mean')
eq(cat['2024']['annual_margin_musd'],10.5,'C03 2024 margin nominal')
eq(cat['2026']['annual_margin_musd'],13.5,'C04 2026 margin nominal')
eq(cat['2024']['gross_margin_minus_model_EL_pp'],5.39,'C05 2024 arith spread')
eq(cat['2026']['gross_margin_minus_model_EL_pp'],4.27,'C06 2026 arith spread')
eq(cat['2024']['gross_margin_minus_model_EL_pp']-cat['2026']['gross_margin_minus_model_EL_pp'],1.12,'C07 spread difference')
ck(cat['2026']['stress'][2]['margin_minus_stressed_EL_and_cost_pp']<0,'C08 stressed 2026 proxy negative')

# 03 / H-FLOW — reported Git result; independent arithmetic/decision check NOT replay.
flow={'events':83,'through_2021':15,'from_2022':68,'central_cost':.0008,
      'mean_central_net':-.0009995546544003969,'mean_gross':-.0001995546544003967,
      'mean_stress_net':-.0016995546544003968,'hit_rate':.39759036144578314,'decision':'KILL_EXPRESSION',
      'sample':'2016-09-12..2026-09-11','git_result_blob':'b4b0460483e1c978d2cc3202df788c0f6a7e5368'}
ck(flow['events']==flow['through_2021']+flow['from_2022'],'F01 population reconciliation')
eq(flow['mean_gross']-flow['central_cost'],flow['mean_central_net'],'F02 net arithmetic')
eq(flow['mean_gross']-.0015,flow['mean_stress_net'],'F03 stressed net arithmetic')
eq(flow['hit_rate'],33/83,'F04 hit count')
ck(flow['mean_central_net']<=0 and flow['decision']=='KILL_EXPRESSION','F05 retain frozen negative decision')

# 04 / H-JOINT — predeclared generic decision-theory synthetic counterexamples.
def act_value(prob_positive,up=.12,down=-.25,information_cost=.0):
    return prob_positive*up+(1-prob_positive)*down-information_cost
threshold=.25/(.12+.25)
ck(act_value(.65)<0 and act_value(.8)>.0,'J01 information may change action (synthetic)')
ck(act_value(.75)>0 and act_value(.8,information_cost=.025)>0,'J02 information may not change action')
ck(act_value(.8,information_cost=.01)>act_value(.65,information_cost=0),'J03 information gain in constructed well calibrated case')
ck(act_value(.6,information_cost=.01)<0,'J04 erroneous confidence gives negative value')
eq(act_value(threshold),0,'J05 explicit decision hurdle')
prior_joint={'macro_vs_static':1.3684049847705118-1.6372718638410766,
             'macro_vs_macro_only':1.3684049847705118-1.5467793954053146,
             'energy_vs_price_only':2.331091-2.385968,
             'energy_vs_macro_only':2.331091-2.535446,
             'energy_vs_static':2.331091-2.276453}
ck(prior_joint['macro_vs_static']<0 and prior_joint['energy_vs_price_only']<0,'J06 prior 2 joint rules do not show positive delta')
ck(prior_joint['energy_vs_static']>0 and prior_joint['energy_vs_price_only']<0,'J07 alternative baseline reverses naive conclusion')

# 05 / H-INDUSTRY — documented issuer figures; possible revenue is NOT incremental profit.
industry={'nexans_framework_meur':600,'nexans_framework_years':7,'nexans_option_years':3,
          'arcelor_ETS_free_gross':212809169,'arcelor_ETS_to_power':72056762,
          'arcelor_verified_emissions':170075530,'eaf_steel_mtons_y':2,
          'reference_CO2_t_per_t':1.73,'eaf_CO2_t_per_t':.60,
          'illustrative_EUA_eur':75,
          'arcelor_Europe_EBITDA_Q2_2026_mUSD':697,'arcelor_Europe_EBITDA_Q3_2026_mUSD':548,
          'arcelor_Europe_EBITDA_Q3_2025_mUSD':513}
industry['nexans_flat_year_meur_UNJUSTIFIED_AS_FORECAST']=600/7
industry['nexans_if_5pct_incremental_margin_meur']=600*.05
industry['ETS_usable_after_declared_transfer']=industry['arcelor_ETS_free_gross']-industry['arcelor_ETS_to_power']
industry['ETS_declared_arithmetic_gap']=industry['arcelor_verified_emissions']-industry['ETS_usable_after_declared_transfer']
industry['ETS_naive_unadjusted_surplus']=industry['arcelor_ETS_free_gross']-industry['arcelor_verified_emissions']
industry['eaf_gross_carbon_value_meur_y']=industry['eaf_steel_mtons_y']*(industry['reference_CO2_t_per_t']-industry['eaf_CO2_t_per_t'])*industry['illustrative_EUA_eur']
eq(industry['ETS_declared_arithmetic_gap'],29323123,'I01 declared ETS arithmetic gap')
eq(industry['ETS_naive_unadjusted_surplus'],42733639,'I02 naive opposite-sign surplus')
ck(industry['ETS_declared_arithmetic_gap']>0 and industry['ETS_naive_unadjusted_surplus']>0,'I03 reporting perimeter changes sign')
eq(industry['eaf_gross_carbon_value_meur_y'],169.5,'I04 carbon physical upper proxy')
eq(industry['nexans_if_5pct_incremental_margin_meur'],30,'I05 illustrative framework margin')
industry['arcelor_Europe_EBITDA_delta_QoQ_mUSD']=548-697
industry['arcelor_Europe_EBITDA_delta_YoY_mUSD']=548-513
eq(industry['arcelor_Europe_EBITDA_delta_QoQ_mUSD'],-149,'I06 Q3 Europe EBITDA down QoQ')
eq(industry['arcelor_Europe_EBITDA_delta_YoY_mUSD'],35,'I07 Q3 Europe EBITDA up YoY')
ck(industry['arcelor_Europe_EBITDA_delta_QoQ_mUSD']<0<industry['arcelor_Europe_EBITDA_delta_YoY_mUSD'],'I08 comparison horizon flips sign')
# Economic P&L + impact cannot be inferred from contract total or accounting allowance.

# 06 / H-IMPLEMENT — French tax/fees structural controlled comparison, no broker fills.
def order_cost(eur=1000,ttf=False,commission_each=1,roundtrip_fx=.0,spread_roundtrip_bps=0):
    return (.004*eur if ttf else 0)+2*commission_each+eur*roundtrip_fx+eur*spread_roundtrip_bps/10000
imple={'nexans_5000_ttf_eur':.004*5000,
       'tr_1000_no_ttf_cost_eur':order_cost(1000),
       'zero_comm_1000_bps20_cost_eur':order_cost(1000,commission_each=0,spread_roundtrip_bps=20),
       'fx_5000_0_5pct_each_eur':5000*.005*2,
       'fx_5000_0_15pct_each_eur':5000*.0015*2}
eq(imple['nexans_5000_ttf_eur'],20,'E01 Nexans tax')
eq(imple['tr_1000_no_ttf_cost_eur'],2,'E02 1EUR x 2 fixed commission')
eq(imple['zero_comm_1000_bps20_cost_eur'],2,'E03 20bps spread offsets 2 EUR commission')
eq(imple['fx_5000_0_5pct_each_eur'],50,'E04 double FX illustrative 0.5pct each')
eq(imple['fx_5000_0_15pct_each_eur'],15,'E05 double FX illustrative 0.15pct each')
ck(order_cost(1000,ttf=True,commission_each=0)>order_cost(1000,ttf=False,commission_each=1),'E06 tax dominates small-ticket fixed fee')

# 07 / H-INTERMEDIARY — Euronext FY2025 accounts + synthetic shareholder multiple compression.
inter={'revenues_mEUR':1823.2,'adj_ebitda_mEUR':1143.1,'net_income_reported_mEUR':642.9,
       'non_volume_share':.59,'q3_2026_share':.55,'q3_2025_share':.60,'eps_reported':6.34,'eps_adjusted':7.27,
       'q3_2026_rev_mEUR':547.4,'q3_2026_adj_ebitda_mEUR':364.2}
inter['ebitda_margin']=inter['adj_ebitda_mEUR']/inter['revenues_mEUR']
inter['non_volume_revenue_mEUR_proxy']=inter['revenues_mEUR']*inter['non_volume_share']
inter['eps_break_even_CAGR_at_PE30_to20_3y']=(30/20)**(1/3)-1
inter['synthetic_10pct_epsgrowth_30to20_return_exdiv']=(1.10**3)*(20/30)-1
inter['q3_2026_margin']=inter['q3_2026_adj_ebitda_mEUR']/inter['q3_2026_rev_mEUR']
eq(inter['ebitda_margin'],.627,'N01 EBITDA/revenue ratio',tol=.001)
ck(inter['eps_adjusted']>inter['eps_reported'],'N02 adjusted EPS cannot replace reported EPS')
ck(inter['synthetic_10pct_epsgrowth_30to20_return_exdiv']<0,'N03 earnings growth may coexist with shareholder price loss')
eq((1+inter['eps_break_even_CAGR_at_PE30_to20_3y'])**3*(20/30),1,'N04 break-even PE compression')
ck(inter['q3_2025_share']>inter['q3_2026_share'],'N05 Q3 YoY nonvol share down')
eq(inter['non_volume_revenue_mEUR_proxy']/680.1,1.57,'N06 nonvol revenue/cost consistency',tol=.02)

# 08 / H-OPTION — synthetic callable bond at premium, 5% coupon, 102 purchase, par 100.
def yield_from_cashflows(cashflows,initial_price):
    def objective(r): return sum(c/(1+r)**(i+1) for i,c in enumerate(cashflows))-initial_price
    return brentq(objective,-.95,1.0)
opt={'price':102,'coupon':5,'principal':100,'call_year':2,'maturity_year':4}
opt['yield_to_call']=yield_from_cashflows([5,105],102)
opt['yield_to_maturity_if_not_called']=yield_from_cashflows([5,5,5,105],102)
opt['annual_coupon_rate_on_par']=.05
ck(opt['yield_to_call']<opt['yield_to_maturity_if_not_called'],'O01 call can lower yield at premium')
ck(opt['yield_to_call']<opt['annual_coupon_rate_on_par'],'O02 coupon exceeds investor IRR')
ck(opt['yield_to_maturity_if_not_called']<opt['annual_coupon_rate_on_par'],'O03 coupon exceeds not-called IRR at premium')
ck(sum(c/(1+opt['yield_to_call'])**(i+1) for i,c in enumerate([5,105]))-102<1e-7,'O04 discounted cash flows reconcile')

# 09 / H-PLATFORM — SEC stock provisions vs flow, not a credit model.
platform={'gross_2026_mUSD':2226+370,'allowance_2026_mUSD':246,
          'gross_2025_mUSD':1621+358,'allowance_2025_mUSD':195,
          'originations_9m_2026_mUSD':4300,'originations_9m_2025_mUSD':2800,
          'interest_fees_9m_2026_mUSD':271,'provisions_9m_2026_mUSD':217,
          'chargeoffs_net_9m_2026_mUSD':166,'chargeoffs_net_9m_2025_mUSD':101,
          'ninety_to_179_days_2026_mUSD':37,'over_180_days_2026_mUSD':157,
          'ninety_to_179_days_2025_mUSD':23,'over_180_days_2025_mUSD':112,
          'loan_reserve_begin_2026_9m_mUSD':195}
platform['net_book_2026']=platform['gross_2026_mUSD']-platform['allowance_2026_mUSD']
platform['net_book_2025']=platform['gross_2025_mUSD']-platform['allowance_2025_mUSD']
platform['coverage_2026']=platform['allowance_2026_mUSD']/platform['gross_2026_mUSD']
platform['coverage_2025']=platform['allowance_2025_mUSD']/platform['gross_2025_mUSD']
platform['origination_growth_9m']=platform['originations_9m_2026_mUSD']/platform['originations_9m_2025_mUSD']-1
platform['misleading_271_minus_217_not_profit']=271-217
eq(platform['net_book_2026'],2350,'P01 net receivable 2026')
eq(platform['net_book_2025'],1784,'P02 net receivable 2025')
eq(platform['coverage_2026'],246/2596,'P03 coverage ratio 2026')
ck(platform['coverage_2026']<platform['coverage_2025'],'P04 coverage stock ratio falls')
eq(platform['origination_growth_9m'],1500/2800,'P05 origination volume grew')
eq(platform['misleading_271_minus_217_not_profit'],54,'P06 subtraction only non-P&L identity')
platform['late_90plus_2026']=37+157
platform['late_90plus_2025']=23+112
platform['late_90plus_share_2026']=platform['late_90plus_2026']/platform['gross_2026_mUSD']
platform['late_90plus_share_2025']=platform['late_90plus_2025']/platform['gross_2025_mUSD']
eq(platform['loan_reserve_begin_2026_9m_mUSD']+217-166,246,'P07 impairment allowance rollforward 9m')
ck(platform['late_90plus_share_2026']>platform['late_90plus_share_2025'],'P08 90+ day delinquency stock share rose')
ck(platform['coverage_2026']<platform['coverage_2025'] and platform['late_90plus_share_2026']>platform['late_90plus_share_2025'],'P09 reserves vs delinquency divergent direction')
eq(platform['late_90plus_2026'],194,'P10 delinquency sum 2026')
eq(platform['late_90plus_2025'],135,'P11 delinquency sum 2025')


# 10 / H-FUNDING — Fed basis: illustrative swap/repo threshold and liquidity-at-risk.
def funded_spread(notional=100_000_000,basis_bp=20,funding_shock_bp=30,equity=5_000_000):
    spread=(basis_bp-funding_shock_bp)/10000
    pnl=notional*spread
    return {'pnl_eur':pnl,'loss_over_equity':pnl/equity,'equity':equity}
fund=funded_spread()
eq(fund['pnl_eur'],-100_000,'U01 basis net is negative after funding shock')
eq(fund['loss_over_equity'],-.02,'U02 levered equity exposure')
# scenario margin call consumes equity (not loss; different accounting)
fund['illustrative_margin_topup_5pct']=.05*100_000_000
ck(fund['illustrative_margin_topup_5pct']>=fund['equity'],'U03 topup exhausts posted equity if no extra liquidity')

# 11 / H-PHYSICAL — commodity storage and power dispatch illustrations.
phys={'wti_may2020_settle_usd_per_barrel':-37.63,'charge_power_eur_mwh':20,'sell_power_eur_mwh':100,'battery_efficiency':.85}
phys['wti_zero_sale_storage_cost20_profit_per_barrel']=37.63-20
phys['wti_zero_sale_storage_cost40_profit_per_barrel']=37.63-40
phys['battery_gross_margin_per_MWh_delivered']=100-20/.85
phys['battery_after_80eur_mwh_all_in_degradation_charge'] = phys['battery_gross_margin_per_MWh_delivered']-80
ck(phys['wti_zero_sale_storage_cost20_profit_per_barrel']>0,'X01 hypothetical cheap storage unlocks positive value')
ck(phys['wti_zero_sale_storage_cost40_profit_per_barrel']<0,'X02 higher storage cost reverses negative-price trade')
ck(phys['battery_after_80eur_mwh_all_in_degradation_charge']<0,'X03 physically profitable spread may fail after costs')

# 12 / H-TAX — French official 2026 PEA>5 years vs CTO PFU, same eligible risk/gain.
# Example gain is realized in 2026; no assumptions that 2026 law persists forever.
tax={'notional_initial_eur':5000,'net_realized_gain_eur':2500,
     'cto_PFU_2026':.314,'pea_5yr_socials_2026':.186,
     'eligible_instrument_and_5yr_age_assumed':True}
tax['cto_after_tax_capital']=tax['notional_initial_eur']+tax['net_realized_gain_eur']*(1-tax['cto_PFU_2026'])
tax['pea_after_tax_capital']=tax['notional_initial_eur']+tax['net_realized_gain_eur']*(1-tax['pea_5yr_socials_2026'])
tax['pea_minus_cto_eur']=tax['pea_after_tax_capital']-tax['cto_after_tax_capital']
ck(tax['pea_after_tax_capital']>tax['cto_after_tax_capital'],'T01 eligible old PEA beats PFU CTA on identical realized positive gain')
eq(tax['pea_minus_cto_eur'],320,'T02 12.8pp differential on 2500 gain')
eq(tax['cto_after_tax_capital'],6715,'T03 CTO example')
eq(tax['pea_after_tax_capital'],7035,'T04 PEA example')
eq((tax['cto_PFU_2026']-tax['pea_5yr_socials_2026'])*100,12.8,'T05 tax rate gap is 12.8 points')

# 12 / H-VIX — previously frozen canonical VX 2013-2021 result: output-only reconciliation.
vix={'trades':36,'years':9,'central_mean_points':.9739861111111111,
     'gross_mean_points':1.073986111111111,'stress_mean_points':.8239861111111111,
     'central_cost_points':.10,'stress_cost_points':.25,
     'worst_trade_points':-14.7,'removed_year':2018,
     'central_mean_ex_largest_year':.736359375,
     'gross_bootstrap_95pct':[-.010736111111111111,2.103805555555554],
     'year_totals_points':{'2013':-2.15,'2014':7.5,'2015':-9.55,'2016':9.5,'2017':1.15,
                           '2018':11.5,'2019':1.2,'2020':6.0,'2021':9.9135},
     'git_blob':'44a792e222f5cd763dcf1becdab9a6eb4d728286'}
vix['mean_from_yearly_totals']=sum(vix['year_totals_points'].values())/vix['trades']
vix['fraction_positive_years']=sum(a>0 for a in vix['year_totals_points'].values())/vix['years']
vix['minimum_equity_for_20pct_max_loss_at_mark_usd']=(-vix['worst_trade_points']*1000)/.2
# This is a necessary but not sufficient buffer for observed endpoint loss, not initial margin.
eq(vix['mean_from_yearly_totals'],vix['central_mean_points'],'V01 yearly totals reconcile')
eq(vix['gross_mean_points']-vix['central_cost_points'],vix['central_mean_points'],'V02 central cost reconciliation')
eq(vix['gross_mean_points']-vix['stress_cost_points'],vix['stress_mean_points'],'V03 stressed cost reconciliation')
eq(vix['fraction_positive_years'],7/9,'V04 year count')
ck(vix['gross_bootstrap_95pct'][0]<0<vix['gross_bootstrap_95pct'][1],'V05 cluster interval spans zero')
eq(vix['minimum_equity_for_20pct_max_loss_at_mark_usd'],73500,'V06 observed loss scales with capital')
ck(vix['central_mean_ex_largest_year']>0,'V07 existing largest-year adversary passes')

# 13 / H-SECTOR-SHOCK and end-month structural results, no recomputation of bars.
sector={'events':722,'negative':360,'positive':362,'gross_mean':.0004154588861753844,
        'central_net':-.00038454111382461555,'central_roundtrip_cost':.0008,
        'worst_return':-.08855273131448801,'git_blob':'03c0176a3363d1980050d43f44712dd42752b551'}
monthend={'events':120,'long_signal':37,'short_signal':83,'minimum_per_side':40,
          'economics_computed':False,'git_blob':'cb7805a102bcfc35d32a60932e560b6298c767ef'}
ck(sector['negative']+sector['positive']==sector['events'],'S01 sector event count')
eq(sector['gross_mean']-sector['central_roundtrip_cost'],sector['central_net'],'S02 sector cost flips gross-positive to net-negative')
ck(sector['gross_mean']>0 and sector['central_net']<0,'S03 trading frictions matter in exact observed setup')
ck(monthend['events']==monthend['long_signal']+monthend['short_signal'],'M01 month-end counts')
ck(monthend['long_signal']<monthend['minimum_per_side'] and not monthend['economics_computed'],'M02 preserve adequacy no-payoff gate')

# 12 / H-PORTFOLIO-RISK — terminal value vs survivable funding. Compounding identity, not market model.
risk={'up':.20,'down':-.20,'arith_mean':(.20-.20)/2,'geo_mean':math.sqrt(1.2*.8)-1}
eq(risk['arith_mean'],0,'R01 arithmetic zero')
ck(risk['geo_mean']<0,'R02 arithmetic zero but geometric negative')
eq((1-.50)*(1+1),1,'R03 50pct loss requires 100pct recovery')

report={'study_id':'QT_H2_5REPORTS_20261122_STRUCTURAL_MECHANISMS_FULL_COVERAGE_V1',
        'as_of':'2026-11-22','class':'REPLAY_EXISTING_RESULTS_PLUS_DOCUMENTARY_AND_SYNTHETIC_STRESS_ONLY',
        'count_executed_assertions':len(checks),'all_pass':True,'assertion_labels':checks,
        'code_vs_market_boundary':'No new historical market payoff simulation, no PIT/OOS, no trading, no proof of actual investment profitability',
        'documented_inputs':{'cat_bonds':'World Bank case studies and 2026 press release',
          'gilt_fire_sales':'Bank of England 2024 Fire sales of safe assets; mechanism not re-estimated',
          'Shopify':'SEC 2026-09-30 10-Q', 'Nexans':'2026-02-04 Nexans/Enedis issuer release',
          'ArcelorMittal':'2026 Q3 SEC results and declared 2021-25 ETS FAQ; no independently verified actual transfer flows',
          'Euronext':'FY2025 investor release + Q3 2026 release',
          'Fed_basis':'Federal Reserve FEDS Note 2026-06-22',
          'PJM':'PJM FTR official description','MBS':'FRBSF and SEC MBS prepayment explanatory documents',
          'France_2026_tax':'impots.gouv.fr PEA after 5 years 18.6pct; economie.gouv.fr PFU 31.4pct'},
        'tests':{
          'H_DRYPOWDER':{'kind':'SYNTHETIC','status':'COST_OF_OPTION_MATERIAL; REAL_EDGE_UNKNOWN','break_even_discount_certain':dcert,'break_even_discount_prob25':dcrit,'grid':dry_grid},
          'H_ILS':{'kind':'DOCUMENTARY_PRIMARY_PLUS_SYNTHETIC_STRESS','status':'PARAMETRIC_INSURANCE_EXISTS; DIRECT_RETAIL_JAMAICA_2026_NOT_ASSUMED','cases':cat},
          'H_FLOW':{'kind':'CANONICAL_RESULT_RECONCILIATION_ONLY','status':'KILL_FROZEN_SPY_TLT_EXPRESSION','result':flow},
          'H_JOINT':{'kind':'CANONICAL_RESULT_RECONCILIATION_PLUS_SYNTHETIC_DECISION','status':'TWO_PRIOR_COMBINATIONS_NO_INCREMENTAL_EDGE','break_even_positive_state_probability':threshold,'prior_result_deltas':prior_joint},
          'H_INDUSTRY':{'kind':'DOCUMENTARY_ACCOUNTING_PLUS_SYNTHETIC_SENSITIVITY','status':'CONTRACT_AND_COST_MECHANISM; EQUITY_VALUE_UNKNOWN','result':industry},
          'H_IMPLEMENT':{'kind':'DOCUMENTARY_TAX_COMMISSION_COST_IDENTITIES','status':'TRANSACTION_COST_EXISTS; REAL_FILLS_UNKNOWN','result':imple},
          'H_INTERMEDIARY':{'kind':'REPORTED_ACCOUNTS_PLUS_SYNTHETIC_VALUATION','status':'REVENUE_FRANCHISE_OBSERVED; SHAREHOLDER_EDGE_UNKNOWN','result':inter},
          'H_OPTION':{'kind':'SYNTHETIC_CASHFLOW_CONTRACT','status':'OPTION_PRICE_MATTERS; HISTORIC_EXCESS_RETURN_UNKNOWN','result':opt},
          'H_PLATFORM':{'kind':'SEC_REPORT_STOCK_VS_FLOW_RECONCILIATION','status':'CREDIT_FRANCHISE_EXISTS; DATA_CAUSAL_VALUE_UNKNOWN','result':platform},
          'H_FUNDING':{'kind':'SYNTHETIC_REPO_MARGIN_PATH','status':'CONVERGENCE_CAN_FAIL_ON_FUNDING_PATH','result':{**fund,'source':'US Federal Reserve 2026'}},
          'H_PHYSICAL':{'kind':'SYNTHETIC_STORAGE_AND_DISPATCH','status':'PHYSICAL_CAPABILITY_CAN_REVERSE_THE_SIGN','result':phys},
          'H_TAX':{'kind':'OFFICIAL_2026_FISCAL_RATES_PLUS_SAME_GAIN_IDENTITY','status':'POSITIVE_TAX_SAVING_IF_ELIGIBLE; SPECIFIC_PORTFOLIO_NOT_TESTED','result':tax},
          'H_VIX':{'kind':'CANONICAL_RESULT_RECONCILIATION_ONLY','status':'PROMOTE_EXPRESSION_ONLY_2013_2021; NOT_ALPHA','result':vix},
          'H_SECTOR_SHOCK':{'kind':'CANONICAL_RESULT_RECONCILIATION_ONLY','status':'KILL_EXACT_EXPRESSION','result':sector},
          'H_MONTHEND':{'kind':'CANONICAL_ADEQUACY_RECONCILIATION_ONLY','status':'PARK_DATA_WITHOUT_PAYOFF','result':monthend},
          'H_RISK':{'kind':'MATH_IDENTITIES','status':'ARITHMETIC_RETURN_NOT_TERMINAL_WEALTH','result':risk},
        },
        'permissions':'READ_ONLY_GITHUB+LOCAL_NON_MARKET_CALCULATIONS; no new economic admission triggered',
        'future_next_witness':'Single PIT dated accessible event with ex-ante instrument + net execution price, use active H2 issue #60; do not tune previously seen ETF/sector trials.'}
output=ROOT/'qt_h2_5rapports_tests_structurels_2026-11-22.json'
output.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'status':'PASS','assertions':len(checks),'report':str(output),
                 'key':{'drypowder_threshold_p25':dcrit,'cat_2026_margin_minus_EL_pp':cat['2026']['gross_margin_minus_model_EL_pp'],
                        'joint_energy_minus_simple':prior_joint['energy_vs_price_only'],
                        'intermediary_PE_break_even_growth':inter['eps_break_even_CAGR_at_PE30_to20_3y'],
                        'callable_YTC':opt['yield_to_call'],'callable_YTM':opt['yield_to_maturity_if_not_called'],
                        'platform_2026_provision_cover':platform['coverage_2026']}},ensure_ascii=False,indent=2))