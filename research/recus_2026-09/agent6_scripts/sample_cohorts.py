"""Agent 6 -- Polymarket liquidity-reward cohort study (bounded, public data only).
PRE-DECLARED DESIGN (written before looking at any outcome):
  Frame  : every wallet receiving a Polymarket REWARD transfer (on-chain, main + secondary reward payers)
           during the daily payout window of D0. Selection is on reward receipt only, never on P&L.
  Cohorts: A  D0=2026-04-15, window [D0, D0+90d)  ;  B  D0=2026-07-01, window [D0, D0+90d) (ends 2026-09-29)
  Tiers  : D0 reward  T1 <$1 | T2 $1-10 | T3 $10-100 | T4 >=$100  (activity-size proxy)
  Sample : 40 wallets per tier per cohort, random.Random(20260929).sample(sorted(tier))
  Metrics: trading P&L ex-rewards = user-pnl(end) - user-pnl(start) (validated: excludes REWARD/MAKER_REBATE)
           rewards / rebates = sum of data-api activity REWARD / MAKER_REBATE paid in (D0+6h, D0+90d+6h]
           net = trading + rewards + rebates ; cash at D0 = USDC.e+pUSD balanceOf at D0 block (capital lower bound)
           window volume = sum TRADE usdcSize in window (capped at 5,000 records -> lower bound)
"""
import json, random, calendar, sys, threading, requests, time
from concurrent.futures import ThreadPoolExecutor
from pmapi import get, DA, activity_all, pnl_series
SEED=20260929; PER_TIER=40
TIERS=[("T1",0,1),("T2",1,10),("T3",10,100),("T4",100,1e12)]
COH={"A":("frame_A_2026-04-15.json",(2026,4,15)),"B":("frame_B_2026-07-01.json",(2026,7,1))}
TOKS=["0x2791bca1f2de4661ed88a30c99a7a9449aa84174","0xc011a7e12a19f7b1f670d46f03b03f3342e82dfb"]
def bal(w,blk):
    tot=0.0
    for t in TOKS:
        for i in range(4):
            try:
                j=requests.post("https://polygon.drpc.org",json={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":t,"data":"0x70a08231"+"0"*24+w[2:]},hex(blk)]},timeout=40).json()
                tot+=int(j["result"],16)/1e6; break
            except Exception: time.sleep(2+i)
        else: return None
    return tot
def pnl_at(series, ts):
    v=None
    for p in series:
        if p["t"]<=ts: v=p["p"]
        else: break
    return v
def one(args):
    coh,tier,w,r0,b0,d0=args
    end=d0+90*86400
    s=sorted(pnl_series(w), key=lambda p:p["t"])
    out={"cohort":coh,"tier":tier,"wallet":w,"d0_reward":r0}
    if not s: out["err"]="no pnl series"; return out
    p0=pnl_at(s,d0); p0flag = p0 is None; p0 = p0 or 0.0
    marks=[pnl_at(s,d0+k*30*86400) for k in range(4)]
    out.update(pnl_start=p0, pnl_start_missing=p0flag, pnl_end=pnl_at(s,end), pnl_marks=marks, pnl_last=s[-1]["p"], series_first=s[0]["t"], series_last=s[-1]["t"])
    acts,st=activity_all(w,start=d0+6*3600,end=end+6*3600,types="REWARD,MAKER_REBATE")
    rw=[0,0,0]; rb=[0,0,0]; R=RB=0.0
    for x in acts:
        k=min(2,int((x["timestamp"]-d0-6*3600)//(30*86400)))
        if x["type"]=="REWARD": R+=x["usdcSize"]; rw[k]+=x["usdcSize"]
        elif x["type"]=="MAKER_REBATE": RB+=x["usdcSize"]; rb[k]+=x["usdcSize"]
    out.update(rewards=R, rebates=RB, rewards_m=rw, rebates_m=rb, reward_status=st, n_reward_days=len({x["timestamp"]//86400 for x in acts if x["type"]=="REWARD"}))
    tr,st2=activity_all(w,start=d0,end=end,types="TRADE",max_records=5000)
    out.update(vol=sum(float(x["usdcSize"] or 0) for x in tr), n_trades=len(tr), vol_status=st2,
               buy=sum(float(x["usdcSize"] or 0) for x in tr if x.get("side")=="BUY"))
    out["cash_d0"]=bal(w,b0)
    lb=get(DA+"/v1/leaderboard",{"user":w,"timePeriod":"ALL"})
    if isinstance(lb,list) and lb: out.update(lb_all_pnl=lb[0].get("pnl"), lb_all_vol=lb[0].get("vol"))
    if out["pnl_end"] is not None: out["trading"]=out["pnl_end"]-p0; out["net"]=out["trading"]+R+RB
    return out
if __name__=="__main__":
    coh=sys.argv[1]; fn,(y,m,d)=COH[coh]; fr=json.load(open(fn)); d0=calendar.timegm((y,m,d,0,0,0))
    jobs=[]
    for t,lo,hi in TIERS:
        members=sorted(w for w,a in fr["reward"].items() if lo<=a<hi)
        pick=random.Random(SEED).sample(members,min(PER_TIER,len(members)))
        print(coh,t,"frame",len(members),"sampled",len(pick),flush=True)
        jobs+=[(coh,t,w,fr["reward"][w],fr["b0"],d0) for w in pick]
    with open(f"results_{coh}.jsonl","w") as f, ThreadPoolExecutor(4) as ex:
        for i,r in enumerate(ex.map(one,jobs)):
            f.write(json.dumps(r)+"\n"); f.flush()
            if i%20==0: print(coh,i,flush=True)
    print("done",coh)
