#!/usr/bin/env node
// Quant-Trade QT_OPEN_CPI_ENERGY_INDUSTRY_20261122_V1 (+ frozen data-gap amendment).
// Exploratory historic simulation, not an OOS or executable performance proof.
// From repository root: node research/edge_lab/discovery/experiments/qt-open-cpi-energy-industry-20261122-run.cjs
'use strict';
const fs=require('node:fs'),path=require('node:path');
const repo=path.resolve(__dirname,'../../../..');
const input=JSON.parse(fs.readFileSync(path.join(__dirname,'qt-open-cpi-energy-industry-20261122-inputs.json'),'utf8'));
const csv=fs.readFileSync(path.join(repo,'data/datasets/us_sector_etf_daily.csv'),'utf8');
const syms=['SPY','XLE','XLI'],prices=new Map(),first=new Map();
for(const row of csv.trim().split(/\r?\n/).slice(1)){
  const [date,sym,open,high,low,close,adj]=row.split(',');
  if(!syms.includes(sym))continue;
  if(!prices.has(date))prices.set(date,{});
  const px=Number(adj);if(!(px>0))throw Error('Nonpositive price '+sym+' '+date);
  prices.get(date)[sym]=px;
  const month=date.slice(0,7);if(!first.has(month)||date<first.get(month))first.set(month,date);
}
function nextMonth(m){const d=new Date(m+'-01T00:00:00Z');d.setUTCMonth(d.getUTCMonth()+1);return d.toISOString().slice(0,7)}
const rows=[];
for(const r of input.rows){
  const entry=first.get(r.ym),exit=first.get(nextMonth(r.ym));
  if(!entry||!exit)throw Error('Missing session '+r.ym);
  if(!(r.reference_etf_date<r.signal_etf_date&&r.signal_etf_date<entry&&entry<exit))throw Error('Future information '+r.ym);
  const old=prices.get(r.reference_etf_date),prev=prices.get(r.signal_etf_date);
  if(!old||!prev)throw Error('Missing historical signal '+r.ym);
  const energyLeads=(prev.XLE/old.XLE)>(prev.XLI/old.XLI);
  if(energyLeads!==r.energy_leads)throw Error('Stock signal does not match frozen input '+r.ym);
  if(Boolean(r.macro_missing)!==(r.inflation_acceleration===null))throw Error('CPI missing inconsistency');
  const begin=prices.get(entry),end=prices.get(exit);
  if(!begin||!end||syms.some(s=>!(begin[s]>0&&end[s]>0)))throw Error('Missing aligned ETF '+r.ym);
  const ratios=syms.map(s=>end[s]/begin[s]);
  rows.push({...r,entry,exit,ratios});
}
if(rows.length!==104||rows[0].ym!=='2018-01'||rows.at(-1).ym!=='2026-08')throw Error('Evaluation period changed');
const select={
  combined:(r,previous)=>r.macro_missing?previous:(r.inflation_acceleration>0&&r.energy_leads),
  macro_only:(r,previous)=>r.macro_missing?previous:(r.inflation_acceleration>0),
  price_only:(r,previous)=>r.energy_leads,
  static_energy:()=>true,
  static_industry:()=>false,
  static_mixed:()=>null
};
const outcome={};
for(const [name,fn] of Object.entries(select)){
  let wealth=1,previousChoice=false,held=[0,0,0],turnover=0,peak=1,drawdown=0,energyMonths=0;
  const returns=[];
  for(const row of rows){
    const current=fn(row,previousChoice);
    if(current!==null)previousChoice=current;
    const target=current===null?[.6,.2,.2]:current?[.6,.4,0]:[.6,0,.4];
    if(Math.abs(target.reduce((a,b)=>a+b,0)-1)>1e-12)throw Error('Non-normalized weights');
    const trade=target.reduce((a,x,i)=>a+Math.abs(x-held[i]),0);
    const gross=target.reduce((a,x,i)=>a+x*row.ratios[i],0);
    const oldWealth=wealth;
    wealth*= (1-trade*0.001)*gross;
    held=target.map((x,i)=>x*row.ratios[i]/gross);
    if(!(wealth>0&&Number.isFinite(wealth)))throw Error('Nonfinite wealth');
    turnover+=trade;
    returns.push(wealth/oldWealth-1);
    if(target[1]>=.399999)energyMonths++;
    peak=Math.max(peak,wealth);drawdown=Math.min(drawdown,wealth/peak-1);
  }
  const CPI=input.US_CPI.entry_index/input.US_CPI.exit_index;
  const real=wealth*CPI;
  const mean=returns.reduce((a,b)=>a+b,0)/returns.length;
  const volatility=Math.sqrt(returns.reduce((a,x)=>a+(x-mean)**2,0)/(returns.length-1))*Math.sqrt(12);
  outcome[name]={
    nominal_wealth:wealth,real_wealth_US_CPI_pre_tax:real,
    real_annualized_growth:Math.pow(real,12/rows.length)-1,
    annualized_monthly_volatility:volatility,
    max_monthly_drawdown:drawdown,
    total_traded_notional_per_1_initial:turnover,
    energy_months:energyMonths
  };
}
const out={
  trial_id:input.id,evidence_level:'HISTORICAL_EXPLORATORY_NOT_GENUINE_PIT_OOS',
  observations:rows.length,missing_macro_months:rows.filter(x=>x.macro_missing).map(x=>x.ym),
  first_entry:rows[0].entry,last_exit:rows.at(-1).exit,
  sources:input.source_blobs,CPI:input.US_CPI,
  signals:{accelerating:rows.filter(x=>x.inflation_acceleration!==null&&x.inflation_acceleration>0).length,energy_leads:rows.filter(x=>x.energy_leads).length,both:rows.filter(x=>x.inflation_acceleration!==null&&x.inflation_acceleration>0&&x.energy_leads).length},
  assumed_cost_bps:10,outcome,
  difference_real:{
    combined_minus_static_mixed:outcome.combined.real_wealth_US_CPI_pre_tax-outcome.static_mixed.real_wealth_US_CPI_pre_tax,
    combined_minus_macro_only:outcome.combined.real_wealth_US_CPI_pre_tax-outcome.macro_only.real_wealth_US_CPI_pre_tax,
    combined_minus_price_only:outcome.combined.real_wealth_US_CPI_pre_tax-outcome.price_only.real_wealth_US_CPI_pre_tax
  }
};
process.stdout.write(JSON.stringify(out,null,2)+'\n');
