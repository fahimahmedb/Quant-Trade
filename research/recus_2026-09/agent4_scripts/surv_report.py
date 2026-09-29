import json,statistics
S=json.load(open("pm_surv.json")); P=json.load(open("pm_positions_surv.json")); U=json.load(open("pm_userpnl_surv.json"))
def q(v,k): 
    v=sorted(v); return round(v[min(len(v)-1,int(len(v)*k))]) if v else None
lines=[]
for fam,v in S.items():
    rows=[]
    for r in v["sample"]:
        a=r["w"]; p=P.get(a); u=U.get(a)
        dead=p["dead"]["cashPnl"] if p else None; live=p["live"]["cashPnl"] if p else None
        famdead=sum(x[1] for c,x in (p["dead_by_class"].items() if p else []) if c==fam)
        corrected_fam=r["fam_realized"]+famdead
        rows.append({"w":a,"trades":r["trades_in_event"],"n_fam":r["n_fam"],"fam_closed":r["fam_realized"],"fam_dead":famdead,"fam_corr":corrected_fam,
                     "all_closed":r["all_realized"],"dead_all":dead,"live_all":live,"u12":u["m12"] if u else None,"uall":u["all"] if u else None,"ufirst":u["first"] if u else None,"trunc":r["trunc"]})
    act=[x for x in rows if x["n_fam"]>0 or x["fam_dead"]!=0]
    fc=[x["fam_corr"] for x in act]; u12=[x["u12"] for x in rows if x["u12"] is not None]
    neg_fc=sum(1 for x in fc if x<0); neg_u=sum(1 for x in u12 if x<0)
    lines.append(f"**{fam}** — participants in the sampled events: {v['n_participants']}; sampled: {len(rows)} most active by trade count (closed-position history capped at 300 per wallet for {sum(1 for x in rows if x['trunc'])} of them, so family P&L below is a lower bound on activity, not on losses).")
    lines.append(f"- Family P&L, closed realized + unredeemed losers (V): losers {neg_fc}/{len(fc)} ({round(100*neg_fc/len(fc)) if fc else None} %), quartiles P10/P25/P50/P75/P90 = {q(fc,.1)} / {q(fc,.25)} / {q(fc,.5)} / {q(fc,.75)} / {q(fc,.9)} $, sum {round(sum(fc)):,} $ (raw closed-only sum was {round(sum(x['fam_closed'] for x in act)):,} $, i.e. {round(100*(1-sum(fc)/sum(x['fam_closed'] for x in act))) if sum(x['fam_closed'] for x in act) else None} % was unbooked losses).")
    lines.append(f"- Whole-wallet user-pnl over 12 months (all families, V): losers {neg_u}/{len(u12)} ({round(100*neg_u/len(u12)) if u12 else None} %), quartiles = {q(u12,.1)} / {q(u12,.25)} / {q(u12,.5)} / {q(u12,.75)} / {q(u12,.9)} $, sum {round(sum(u12)):,} $.")
    top=sorted(act,key=lambda x:-x["fam_corr"])[:5]
    lines.append("- Top 5 corrected family P&L: "+"; ".join(f"`{x['w'][:6]}…{x['w'][-4:]}` {round(x['fam_corr']):,} $ (u12 {x['u12']})" for x in top)+".")
    bot=sorted(act,key=lambda x:x["fam_corr"])[:3]
    lines.append("- Bottom 3: "+"; ".join(f"`{x['w'][:6]}…{x['w'][-4:]}` {round(x['fam_corr']):,} $ (u12 {x['u12']})" for x in bot)+".")
    lines.append("")
out="## 4. Survivorship sample (losers of the same mechanism)\n\nMethod (V): every wallet that traded in three September-2026 box-office events (Forgotten Island, Heart of the Beast, Primetime opening weekends) and in the September-2026 monthly tweet-count event was enumerated from `trades`; the 70 most active per family were pulled (`closed-positions` up to 300, `positions` for unredeemed losers, `user-pnl` 12 m). Selection is by activity, not by P&L, so it includes losers; it still over-weights active accounts.\n\n"+"\n".join(lines)
open("surv_section.md","w").write(out); print(out)
