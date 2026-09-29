import json,datetime,collections,statistics
d=json.load(open("pm_deep.json"))
def ym(ts): return datetime.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m")
cut=datetime.datetime(2025,9,29).timestamp()
fam_agg=collections.defaultdict(lambda: collections.defaultdict(float))
for a,w in d.items():
    fam=w["label"].split()[0]; P=w["positions"]
    famP=[p for p in P if p["c"]==("TWEETS" if fam=="TWEETS" else "BOXOFFICE" if fam=="BOX" else "MUSIC" if fam=="MUSIC" else "AI_TECH" if fam=="AI" else "MENTIONS")]
    r12=sum(p["r"] for p in famP if p["ts"] and int(p["ts"])>=cut); b12=sum(p["b"] for p in famP if p["ts"] and int(p["ts"])>=cut)
    rall=sum(p["r"] for p in famP); ball=sum(p["b"] for p in famP)
    months=collections.defaultdict(float); mb=collections.defaultdict(float)
    for p in famP:
        if p["ts"]: months[ym(p["ts"])]+=p["r"]; mb[ym(p["ts"])]+=p["b"]
    ms=sorted(months)
    last6=[(m,round(months[m])) for m in ms[-6:]]
    win=sum(1 for p in famP if p["r"]>0); n=len(famP)
    hi=[p for p in famP if p["ap"]>=0.9]; hir=sum(p["r"] for p in hi); hib=sum(p["b"] for p in hi)
    lo=[p for p in famP if p["ap"]<=0.15]; lor=sum(p["r"] for p in lo); lob=sum(p["b"] for p in lo)
    top1=max((p["r"] for p in famP),default=0)
    # concentration: share of top 5 positions in total fam realized (if positive)
    tops=sorted((p["r"] for p in famP),reverse=True)[:5]; conc=round(sum(tops)/rall,2) if rall>0 else None
    # two-sided detection: same title with both Yes and No positions
    byt=collections.defaultdict(set)
    for p in famP: byt[p["t"]].add(p["o"])
    two=sum(1 for s in byt.values() if len(s)>=2); nmk=len(byt)
    avg_size=round(ball/n) if n else None
    top_titles=sorted(famP,key=lambda p:-p["r"])[:4]
    print(f"  markets={nmk} two-sided={two} ({round(100*two/nmk) if nmk else None}%) avg_bought/pos=${avg_size}")
    for p in top_titles: print(f"     +{round(p['r'])} ap={p['ap']:.2f} b={round(p['b'])} {p['o']} | {p['t'][:80]} | {datetime.datetime.utcfromtimestamp(int(p['ts'])).strftime('%Y-%m-%d') if p['ts'] else ''}")
    up=w["user_pnl"]; 
    if up:
        pts=[(x.get("t"),x.get("p")) for x in up]; last=pts[-1][1]; first=pts[0][1]
        # value 12 months ago
        v12=[p for t,p in pts if t and int(t)>=cut]; pnl12=(last-v12[0]) if v12 else None
        peak=max(p for _,p in pts); dd=round(last-peak)
        first_t=datetime.datetime.utcfromtimestamp(int(pts[0][0])).strftime("%Y-%m-%d") if pts[0][0] else None
    else: last=pnl12=dd=first_t=None
    print(f"\n[{w['label']}] {a}\n  fam positions n={n} (all pulled={w['n']}{' TRUNC' if w['truncated'] else ''}) win%={round(100*win/n) if n else None} | fam realized ALL={round(rall)} on bought {round(ball)} (ret {round(rall/ball,3) if ball else None}) | 12m={round(r12)} on {round(b12)} (ret {round(r12/b12,3) if b12 else None})")
    print(f"  months(last6)={last6} | top1={round(top1)} top5share={conc} | hi90 n={len(hi)} r={round(hir)} b={round(hib)} ret={round(hir/hib,3) if hib else None} | lo15 n={len(lo)} r={round(lor)} b={round(lob)}")
    print(f"  user-pnl: first={first_t} last={round(last) if last is not None else None} 12m={round(pnl12) if pnl12 is not None else None} dd_from_peak={dd} | rewards={w['reward_sum']}({w['reward_n']}) rebates={w['rebate_sum']}({w['rebate_n']}) | other-class realized={round(sum(p['r'] for p in P)-rall)}")
    fa=fam_agg[fam]; fa["n_wallets"]+=1; fa["r12"]+=r12; fa["b12"]+=b12; fa["rall"]+=rall; fa["hi_r"]+=hir; fa["hi_b"]+=hib; fa["lo_r"]+=lor; fa["lo_b"]+=lob; fa["pos"]+=n
print("\n=== family aggregates ===")
for f,v in fam_agg.items(): print(f, {k:round(x) for k,x in v.items()}, "ret12=",round(v["r12"]/v["b12"],3) if v["b12"] else None, "hi90ret=",round(v["hi_r"]/v["hi_b"],3) if v["hi_b"] else None, "lo15ret=",round(v["lo_r"]/v["lo_b"],3) if v["lo_b"] else None)
