#!/usr/bin/env node
// Quant-Trade QT_OPEN_MACRO_CROSSASSET_20261122_V1
// Exploratory historical economic comparison; NOT PIT-certified, NOT an AI-edge proof.
// Usage from repository root: node research/edge_lab/discovery/experiments/qt-open-macro-crossasset-20261122-run.cjs
'use strict';
const fs = require('node:fs');
const path = require('node:path');

const ROOT = path.resolve(__dirname, '../../../..');
const input = JSON.parse(fs.readFileSync(path.join(__dirname, 'qt-open-macro-crossasset-20261122-inputs.json'), 'utf8'));
const csv = fs.readFileSync(path.join(ROOT, 'data/datasets/us_sector_etf_daily.csv'), 'utf8');
const prices = new Map();
const first = new Map();
const symbols = ['SPY','TLT','GLD'];
for (const line of csv.trim().split(/\r?\n/).slice(1)) {
  const [date, symbol, open, high, low, close, adjusted] = line.split(',');
  if (!symbols.includes(symbol)) continue;
  const value = Number(adjusted);
  if (!(value > 0)) throw new Error('Invalid adjusted price '+date+' '+symbol);
  if (!prices.has(date)) prices.set(date, {});
  prices.get(date)[symbol] = value;
  const month = date.slice(0,7);
  if (!first.has(month) || date < first.get(month)) first.set(month,date);
}
function monthAfter(month) {
  const d = new Date(month+'-01T00:00:00Z');
  d.setUTCMonth(d.getUTCMonth()+1);
  return d.toISOString().slice(0,7);
}
function olderBy(date,days) {
  const d = new Date(date+'T00:00:00Z');
  d.setUTCDate(d.getUTCDate()-days);
  return d.toISOString().slice(0,10);
}
const months = [];
for (const r of input.records) {
  const entry = first.get(r.month), exit = first.get(monthAfter(r.month));
  if (!entry || !exit) throw new Error('Missing first ETF close '+r.month);
  if (!(r.signal_etf_date < entry && r.macro_date <= olderBy(r.signal_etf_date,5) &&
        r.spy_6m_reference < r.signal_etf_date && exit > entry)) throw new Error('LOOKAHEAD '+r.month);
  if (Math.abs(prices.get(r.signal_etf_date).SPY/prices.get(r.spy_6m_reference).SPY-1-r.spy_6m_momentum)>1e-12)
    throw new Error('Source snapshot mismatch '+r.month);
  const source = prices.get(entry), dest = prices.get(exit);
  if (!source || !dest || symbols.some(s => !(source[s] > 0 && dest[s] > 0)))
    throw new Error('Unaligned ETF closes '+r.month);
  months.push({...r,entry,exit,ratios:Object.fromEntries(symbols.map(s=>[s,dest[s]/source[s]]))});
}
if (months.length!==44 || months[0].month!=='2023-01' || months.at(-1).month!=='2026-08')
  throw new Error('Frozen evaluation window mismatch');
const arms = {
  combined: r => ({SPY:.6,TLT:r.inverted&&r.downtrend?0:.4,GLD:r.inverted&&r.downtrend?.4:0}),
  macro_only:r => ({SPY:.6,TLT:r.inverted?0:.4,GLD:r.inverted?.4:0}),
  trend_only:r => ({SPY:.6,TLT:r.downtrend?0:.4,GLD:r.downtrend?.4:0}),
  static_tlt:r => ({SPY:.6,TLT:.4,GLD:0}),
  static_gold:r => ({SPY:.6,TLT:0,GLD:.4}),
  static_mixed:r => ({SPY:.6,TLT:.2,GLD:.2})
};
const outcomes = {};
for (const [name,policy] of Object.entries(arms)) {
  let wealth=1,held={SPY:0,TLT:0,GLD:0},turnover=0,GLD_months=0,peak=1,max_drawdown=0;
  const monthly_returns=[];
  for (const month of months) {
    const target=policy(month);
    if (Math.abs(symbols.reduce((a,s)=>a+target[s],0)-1)>1e-12 ||
        symbols.some(s=>target[s]<0)) throw new Error('Bad weights');
    const traded=symbols.reduce((a,s)=>a+Math.abs(target[s]-held[s]),0);
    const cost=traded*10/10000;
    const gross=symbols.reduce((a,s)=>a+target[s]*month.ratios[s],0);
    if (!(gross>0 && cost<1)) throw new Error('Bad gross/cost');
    const old=wealth;
    wealth=wealth*(1-cost)*gross;
    monthly_returns.push(wealth/old-1);
    held=Object.fromEntries(symbols.map(s=>[s,target[s]*month.ratios[s]/gross]));
    turnover+=traded;
    if (target.GLD>=.399999) GLD_months++;
    peak=Math.max(peak,wealth);
    max_drawdown=Math.min(max_drawdown,wealth/peak-1);
  }
  const n=months.length,years=n/12;
  const mean=monthly_returns.reduce((a,b)=>a+b,0)/n;
  const stdev=Math.sqrt(monthly_returns.reduce((a,b)=>a+(b-mean)**2,0)/(n-1))*Math.sqrt(12);
  const cpi=input.CPI_US.start_index/input.CPI_US.end_index;
  const real=wealth*cpi;
  outcomes[name]={
    terminal_nominal_wealth:wealth,
    terminal_real_US_CPI_pre_tax:real,
    real_annualized_growth:Math.pow(real,1/years)-1,
    annualized_monthly_volatility:stdev,
    max_monthly_drawdown,
    total_traded_notional_per_1_initial:turnover,
    GLD_months,
    observations:n
  };
}
const result={
  trial_id:input.id,
  evidence_level:'EXPLORATORY_HISTORICAL_PRE_TAX_NOT_PIT_CERTIFIED',
  funds_traded:'NONE',
  assumed_cost_bps_per_dollar:10,
  months:months.length,
  first_entry:months[0].entry,
  last_exit:months.at(-1).exit,
  signals:{inverted_months:months.filter(r=>r.inverted).length,downtrend_months:months.filter(r=>r.downtrend).length,combined_GLD_months:months.filter(r=>r.inverted&&r.downtrend).length},
  sources:input.source_blobs,
  CPI:input.CPI_US,
  outcomes,
  pairwise_real:{
    combined_minus_static_mixed:outcomes.combined.terminal_real_US_CPI_pre_tax-outcomes.static_mixed.terminal_real_US_CPI_pre_tax,
    combined_minus_macro_only:outcomes.combined.terminal_real_US_CPI_pre_tax-outcomes.macro_only.terminal_real_US_CPI_pre_tax,
    combined_minus_trend_only:outcomes.combined.terminal_real_US_CPI_pre_tax-outcomes.trend_only.terminal_real_US_CPI_pre_tax
  }
};
process.stdout.write(JSON.stringify(result,null,2)+'\n');
