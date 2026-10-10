"""One frozen FX proxy experiment. Streaming state, no transport or execution API.

All market I/O belongs to the gated runner. No parameter grid or candidate
selection. Synthetic clients may supply explicit past state to challenge it.
"""
from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from datetime import datetime, timedelta, timezone
import json
import math

from safety_kernel import (Quote, Costs, CENTRAL, STRESS, PIP, sides,
    opening_fill, closing_fill, planned_quantity, fill_admissible,
    rollover_charge)

UTC = timezone.utc
BAR_MS = 900000
WARMUP_START = int(datetime(2025, 1, 1, 5, tzinfo=UTC).timestamp()*1000)
START = int(datetime(2025, 2, 1, tzinfo=UTC).timestamp()*1000)
END = int(datetime(2026, 10, 1, tzinfo=UTC).timestamp()*1000)
SPLIT = "2025-12-01"
EXPRESSIONS = ("MAIN", "NO_ADDS", "STATIC_GRID")


def dt(ms):
    return datetime.fromtimestamp(ms/1000, UTC)


def at(day, hour):
    return int(datetime.fromisoformat(day).replace(hour=hour, tzinfo=UTC).timestamp()*1000)


def next_rollover(time):
    from zoneinfo import ZoneInfo
    ny=ZoneInfo("America/New_York")
    current=dt(time).astimezone(ny)
    roll=current.replace(hour=17,minute=0,second=0,microsecond=0)
    if roll<=current:roll+=timedelta(days=1)
    return int(roll.timestamp()*1000)


@dataclass
class Bar:
    end: int
    high: float
    low: float
    close: float


@dataclass
class BarBuilder:
    start: int
    first: int | None = None
    last: int | None = None
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    max_gap: int = 0

    def add(self, q):
        if not self.start <= q.time_ms < self.start + BAR_MS:
            raise ValueError("quote outside open bar")
        if self.first is None:
            self.first = q.time_ms
            self.high = self.low = q.mid
        else:
            self.max_gap = max(self.max_gap, q.time_ms-self.last)
            self.high, self.low = max(self.high,q.mid), min(self.low,q.mid)
        self.last, self.close = q.time_ms, q.mid

    def finish(self):
        if (self.first is None or self.first-self.start > 60000
                or self.start+BAR_MS-self.last > 60000 or self.max_gap > 60000):
            return None
        return Bar(self.start+BAR_MS,self.high,self.low,self.close)


@dataclass
class Indicators:
    previous: Bar | None = None
    count: int = 0
    gain: float = 0.0
    loss: float = 0.0
    tr: float = 0.0
    plus: float = 0.0
    minus: float = 0.0
    dx_count: int = 0
    adx: float | None = None
    dx_sum: float = 0.0
    rsi: float | None = None

    def reset(self):
        fresh = Indicators()
        for f in fields(self):
            setattr(self,f.name,getattr(fresh,f.name))

    def update(self, bar):
        old_rsi = self.rsi
        if self.previous is None:
            self.previous=bar
            return None, None, None, None
        prev=self.previous
        if bar.end-prev.end != BAR_MS:
            raise ValueError("caller must reset missing bar")
        change=bar.close-prev.close
        gain,loss=max(change,0),max(-change,0)
        tr=max(bar.high-bar.low,abs(bar.high-prev.close),abs(bar.low-prev.close))
        up,down=bar.high-prev.high,prev.low-bar.low
        plus=up if up>0 and up>down else 0.0
        minus=down if down>0 and down>up else 0.0
        self.count+=1
        if self.count <= 14:
            self.gain+=gain/14; self.loss+=loss/14
            self.tr+=tr/14; self.plus+=plus/14; self.minus+=minus/14
        else:
            for name,value in (("gain",gain),("loss",loss),("tr",tr),
                               ("plus",plus),("minus",minus)):
                setattr(self,name,(13*getattr(self,name)+value)/14)
        if self.count >= 14:
            self.rsi=(50.0 if self.gain==self.loss==0 else 100.0 if self.loss==0
                      else 100-100/(1+self.gain/self.loss))
            total=self.plus+self.minus
            dx=0.0 if total==0 else 100*abs(self.plus-self.minus)/total
            self.dx_count+=1
            if self.dx_count <= 14:
                self.dx_sum+=dx
                if self.dx_count==14:self.adx=self.dx_sum/14
            else:
                self.adx=(13*self.adx+dx)/14
        self.previous=bar
        return old_rsi,self.rsi,self.adx,math.log(bar.close/prev.close)


@dataclass
class Order:
    kind: str
    intent: Quote
    source_time: int
    reason: str
    rung: int = 0
    stop_bound: bool = False


@dataclass
class Basket:
    direction: int
    anchor: float
    spacing: float
    stop: float
    target: float
    risk: float
    quantity: int
    rungs: int
    signal_time: int
    entries: list = field(default_factory=list)
    next_rung: int = 1
    first_fill: int | None = None
    finance_cursor: int | None = None
    next_rollover_ms: int | None = None
    commission: float = 0.0
    financing: float = 0.0
    rollovers: int = 0
    spread_cost: float = 0.0
    slippage_cost: float = 0.0
    pending: Order | None = None
    fills: list = field(default_factory=list)
    skipped_adds: list = field(default_factory=list)

    @property
    def units(self):
        return sum(x[0] for x in self.entries)


@dataclass
class Path:
    expression: str
    costs: Costs
    cash: float = 100000.0
    peak: float = 100000.0
    max_drawdown: float = 0.0
    day_equity: float = 100000.0
    current_day: str = ""
    basket: Basket | None = None
    disabled: bool = False
    risk_failures: list = field(default_factory=list)
    cancellations: list = field(default_factory=list)
    completed: list = field(default_factory=list)
    calendar_nav: dict = field(default_factory=dict)
    commission: float = 0.0
    financing: float = 0.0
    spread_cost: float = 0.0
    slippage_cost: float = 0.0
    exposure_ms_units: float = 0.0
    exposure_cursor: int | None = None

    def nav(self, q, *, unresolved=False):
        b=self.basket
        if b is None or not b.units:return self.cash
        bid,ask=sides(q,self.costs)
        px=bid if b.direction==1 else ask
        if unresolved or (b.pending and b.pending.stop_bound):
            px=min(px,b.stop) if b.direction==1 else max(px,b.stop)
        px-=b.direction*self.costs.slippage
        return (self.cash+sum(n*b.direction*(px-p) for n,p in b.entries)
                -b.units*self.costs.commission)

    def mark(self,q):
        nav=self.nav(q)
        self.peak=max(self.peak,nav)
        self.max_drawdown=max(self.max_drawdown,(self.peak-nav)/self.peak)
        return nav

    def request_close(self,time,q,reason,*,stop_bound=False):
        b=self.basket
        if b is None or not b.units:
            self.basket=None
            return
        if b.pending and b.pending.kind=="CLOSE":
            # Keep the earliest eligibility; adverse stop overrides its price bound.
            if stop_bound:
                b.pending.stop_bound=True
                b.pending.reason=reason
            return
        b.pending=Order("CLOSE",Quote(time,q.bid,q.ask),q.time_ms,reason,
                        stop_bound=stop_bound)

    def clock(self,time,last):
        b=self.basket
        if b and b.units:
            if self.exposure_cursor is not None:
                self.exposure_ms_units+=(time-self.exposure_cursor)*b.units
            self.exposure_cursor=time
            charge,count=0.0,0
            if time>=b.next_rollover_ms:
                charge,count=rollover_charge(dt(b.finance_cursor),dt(time),b.units,self.costs)
                b.next_rollover_ms=next_rollover(time)
            self.cash-=charge; self.financing+=charge; b.financing+=charge
            b.rollovers+=count; b.finance_cursor=time
            if count and "ROLLOVER" not in self.risk_failures:
                self.risk_failures.append("ROLLOVER")
            deadlines=[(last.time_ms+5000,"STALE",True),
                       (b.first_fill+7200000,"TIME",False),
                       (at(dt(b.signal_time).date().isoformat(),16),"CUTOFF",False)]
            # Timers use only the last already-known quote, never the next price.
            for due,reason,bound in sorted(deadlines,key=lambda x:x[0]):
                if due<time or (due==time and reason!="STALE"):
                    self.request_close(due,last,reason,stop_bound=bound)
        day=dt(time).date().isoformat()
        if day!=self.current_day:
            self.current_day=day
            self.day_equity=self.nav(last) if last else self.cash

    def opportunity(self,time,last,direction,anchor,sigma,reference):
        if self.disabled or self.basket is not None:return
        if last is None or time-last.time_ms>5000:
            self.cancellations.append([time,"STALE_ENTRY"]);return
        d=anchor*(reference if self.expression=="STATIC_GRID" else sigma)
        if (not math.isfinite(d) or d<=0 or sigma<=0
                or round(last.ask-last.bid,12)>min(PIP,.2*d)):
            self.cancellations.append([time,"SPREAD_OR_VOLATILITY"]);return
        risk=.0025*self.day_equity
        if self.expression!="STATIC_GRID":risk*=min(1,reference/sigma)
        k=1 if self.expression=="NO_ADDS" else 3
        try:q=planned_quantity(self.day_equity,anchor,d,risk,k)
        except ValueError:
            self.cancellations.append([time,"INVALID_PLAN"]);return
        if q<1:
            self.cancellations.append([time,"SUB_UNIT_PLAN"]);return
        self.basket=Basket(direction,anchor,d,anchor-direction*3*d,
            anchor+direction*d/2,risk,q,k,time,
            pending=Order("OPEN",Quote(time,last.bid,last.ask),last.time_ms,"SIGNAL"))

    def _execution_detail(self,o,q,price):
        b=self.basket;s=b.direction
        candidates=[]
        for book in (o.intent,q):
            bid,ask=sides(book,self.costs)
            px=(ask if s==1 else bid) if o.kind=="OPEN" else (bid if s==1 else ask)
            candidates.append((px,book.mid,abs(px-book.mid),book.time_ms))
        choose_max=(s==1)==(o.kind=="OPEN")
        selected=(max if choose_max else min)(candidates,key=lambda x:x[0])
        if o.kind=="CLOSE" and o.stop_bound:
            if (s==1 and b.stop<selected[0]) or (s==-1 and b.stop>selected[0]):
                selected=(b.stop,b.stop,0.0,None)
        return {"intent_ms":o.intent.time_ms,"source_ms":o.source_time,
                "fill_ms":q.time_ms,"rung":o.rung,"reason":o.reason,
                "kind":o.kind,"price":price,"mid_reference":selected[1],
                "spread_per_unit":selected[2],"slippage_per_unit":self.costs.slippage,
                "reference_quote_ms":selected[3]}

    def on_quote(self,q,last):
        b=self.basket
        if b is None:return
        if b.units:
            liquid=q.bid if b.direction==1 else q.ask
            stop_hit=b.direction*(liquid-b.stop)<=0
            nav=self.mark(q)
            dd=(self.peak-nav)/self.peak
            gross=b.units*q.mid
            if stop_hit:self.request_close(q.time_ms,q,"STOP",stop_bound=True)
            if dd>=.05:
                self.disabled=True
                if "DRAWDOWN" not in self.risk_failures:self.risk_failures.append("DRAWDOWN")
                self.request_close(q.time_ms,q,"DRAWDOWN")
            if nav<=0 or gross/30>.05*nav:
                if "MARGIN" not in self.risk_failures:self.risk_failures.append("MARGIN")
                self.request_close(q.time_ms,q,"MARGIN")
            if (not b.pending or b.pending.kind!="CLOSE") and b.direction*(liquid-b.target)>=0:
                self.request_close(q.time_ms,q,"TARGET")
        o=b.pending
        if o is not None:
            if q.time_ms<o.intent.time_ms+1000:return
            if o.kind=="CLOSE":
                price=closing_fill(o.intent,q,b.direction,self.costs,
                                   stop=b.stop if o.stop_bound else None)
                detail=self._execution_detail(o,q,price);detail["units"]=b.units
                pnl=sum(n*b.direction*(price-p) for n,p in b.entries)
                fee=b.units*self.costs.commission
                self.cash+=pnl-fee;self.commission+=fee;b.commission+=fee
                spread=b.units*detail["spread_per_unit"]
                slip=b.units*self.costs.slippage
                self.spread_cost+=spread;b.spread_cost+=spread
                self.slippage_cost+=slip;b.slippage_cost+=slip
                b.fills.append(detail)
                record={"signal_ms":b.signal_time,"first_fill_ms":b.first_fill,
                    "exit_ms":q.time_ms,"direction":b.direction,"anchor":b.anchor,
                    "spacing":b.spacing,"risk_budget":b.risk,"fixed_stop":b.stop,
                    "fixed_target":b.target,"rung_units":b.quantity,
                    "fills":b.fills,"skipped_adds":b.skipped_adds,
                    "net_pnl":pnl-b.commission-b.financing,
                    "commission":b.commission,"financing":b.financing,
                    "spread_cost":b.spread_cost,"slippage_cost":b.slippage_cost,
                    "gross_mid_pnl":pnl+b.spread_cost+b.slippage_cost,
                    "rollovers":b.rollovers,"close_reason":o.reason}
                self.completed.append(record)
                self.basket=None;self.exposure_cursor=None
                self.mark(q)
                return
            price=opening_fill(o.intent,q,b.direction,self.costs)
            bid,ask=sides(q,self.costs)
            liquidation=(bid if b.direction==1 else ask)-b.direction*self.costs.slippage
            proposed_nav=(self.nav(q)-b.quantity*(b.direction*(price-liquidation)+2*self.costs.commission)
                          if price is not None else 0.0)
            accepted=(price is not None and fill_admissible(b.entries,b.quantity,
                price,b.stop,b.direction,b.commission,b.risk,proposed_nav,q.mid))
            if not accepted:
                if o.rung==0:
                    self.cancellations.append([b.signal_time,"EXPIRED_OR_RISK_ENTRY"])
                    self.basket=None
                else:
                    b.skipped_adds.append([o.rung,q.time_ms,"EXPIRED_OR_RISK_ADD"])
                    b.pending=None
                return
            detail=self._execution_detail(o,q,price);detail["units"]=b.quantity
            fee=b.quantity*self.costs.commission
            b.commission+=fee;self.commission+=fee;self.cash-=fee
            spread=b.quantity*detail["spread_per_unit"];slip=b.quantity*self.costs.slippage
            b.spread_cost+=spread;self.spread_cost+=spread
            b.slippage_cost+=slip;self.slippage_cost+=slip
            b.entries.append((b.quantity,price));b.fills.append(detail);b.pending=None
            if b.first_fill is None:
                b.first_fill=q.time_ms;b.finance_cursor=q.time_ms;self.exposure_cursor=q.time_ms
                b.next_rollover_ms=next_rollover(q.time_ms)
            nav=self.mark(q)
            if (self.peak-nav)/self.peak>=.05:
                self.disabled=True
                if "DRAWDOWN" not in self.risk_failures:self.risk_failures.append("DRAWDOWN")
                self.request_close(q.time_ms,q,"DRAWDOWN")
            return  # This group cannot execute or trigger a second rung.
        if not b.units or b.next_rung>=b.rungs:return
        rung=b.next_rung;level=b.anchor-b.direction*rung*b.spacing
        hit=q.ask<=level if b.direction==1 else q.bid>=level
        if hit:
            b.next_rung+=1
            b.pending=Order("OPEN",q,q.time_ms,"ADD",rung)


@dataclass
class Engine:
    indicators: Indicators = field(default_factory=Indicators)
    builder: BarBuilder | None = None
    last: Quote | None = None
    variance: float | None = None
    reference: float | None = None
    warmup_returns: list = field(default_factory=list)
    warmup_done: bool = False
    warmup_state: dict | None = None
    paths: list = field(default_factory=lambda:[Path(e,c) for e in EXPRESSIONS for c in (CENTRAL,STRESS)])
    used_days: list = field(default_factory=list)
    opportunities: list = field(default_factory=list)
    coverage: dict = field(default_factory=dict)
    invalid_bars: int = 0
    groups: int = 0
    last_group_ms: int | None = None
    finalized: bool = False

    def finish_warmup(self):
        if self.warmup_done:return
        rs=self.warmup_returns
        if len(rs)<1000:raise ValueError("SOURCE_WARMUP_TOO_SHORT")
        self.reference=math.sqrt(math.fsum(r*r for r in rs)/len(rs))
        self.variance=math.fsum(r*r for r in rs[:96])/96
        for r in rs[96:]:self.variance=.94*self.variance+.06*r*r
        if self.reference<=0 or self.variance<=0:raise ValueError("SOURCE_WARMUP_ZERO_VARIANCE")
        self.warmup_returns=[];self.warmup_done=True

    def on_bar(self,end,bar):
        if START<=end-1<END:
            t=dt(end-1);day=t.date().isoformat()
            if t.weekday()<5 and 7<=t.hour<16:
                self.coverage[day]=self.coverage.get(day,0)+int(bar is not None)
        if bar is None:
            self.indicators.reset();self.invalid_bars+=1
        else:
            old,rsi,adx,r=self.indicators.update(bar)
            if r is not None:
                if end<=START:self.warmup_returns.append(r)
                elif self.warmup_done:self.variance=.94*self.variance+.06*r*r
            if START<end<END and self.warmup_done:
                t=dt(end);day=t.date().isoformat()
                direction=0
                if old is not None and rsi is not None and adx is not None and adx<20:
                    direction=1 if old<=30<rsi else -1 if old>=70>rsi else 0
                if direction and t.weekday()<5 and 7<=t.hour<14 and day not in self.used_days:
                    self.used_days.append(day)
                    sigma=math.sqrt(self.variance)
                    self.opportunities.append([end,direction,bar.close,sigma])
                    for p in self.paths:p.opportunity(end,self.last,direction,bar.close,sigma,self.reference)
        if end==START:
            self.finish_warmup()
            self.warmup_state={"reference":self.reference,"variance":self.variance,
                "indicators":encode(self.indicators),"last_source_group":encode(self.last),
                "utc_warmup_end_ms":START,"all_data_strictly_before_utc_outcome":True}

    def _clock(self,time):
        if time<START:return
        for p in self.paths:
            if p.basket is None and time%BAR_MS!=0:continue
            p.clock(time,self.last)
            if self.last:p.mark(self.last)
            if time%(86400000)==0 and time>START:
                p.calendar_nav[(dt(time)-timedelta(days=1)).date().isoformat()]=p.nav(self.last)

    def feed(self,q,*,warmup_sink=None):
        if self.finalized:raise ValueError("finalized experiment")
        if not WARMUP_START<=q.time_ms<END:raise ValueError("quote outside manifest UTC bounds")
        if self.last_group_ms is not None and q.time_ms<=self.last_group_ms:
            raise ValueError("groups must be strictly chronological")
        if self.builder is None:self.builder=BarBuilder(WARMUP_START)
        while q.time_ms>=self.builder.start+BAR_MS:
            end=self.builder.start+BAR_MS
            self._clock(end)
            self.on_bar(end,self.builder.finish())
            if end==START and warmup_sink is not None:warmup_sink(self.warmup_state)
            self.builder=BarBuilder(end)
        self._clock(q.time_ms)
        if q.time_ms>=START:
            for p in self.paths:p.on_quote(q,self.last)
        self.builder.add(q)
        self.last=q;self.last_group_ms=q.time_ms;self.groups+=1

    def finalize(self):
        if self.finalized:raise ValueError("cannot finalize twice")
        if self.builder is None:raise ValueError("SOURCE_NO_ROWS")
        while self.builder.start+BAR_MS<=END:
            end=self.builder.start+BAR_MS
            self._clock(end)
            self.on_bar(end,self.builder.finish())
            self.builder=BarBuilder(end)
        self.finalized=True
        for p in self.paths:
            # No fabricated end-window quote. Residual exposure is preserved.
            if p.basket and not p.basket.units:p.basket=None
            if p.basket:
                p.calendar_nav["2026-09-30"]=p.nav(self.last,unresolved=True)
        return self.result()

    def result(self):
        days=[];date=dt(START).date();end=dt(END).date()
        while date<end:
            if date.weekday()<5:days.append(date.isoformat())
            date+=timedelta(days=1)
        unqualified=[d for d in days if self.coverage.get(d,0)/36<.90]
        paths={}
        for p in self.paths:
            name=p.expression+("_CENTRAL" if p.costs==CENTRAL else "_STRESS")
            previous=100000.0;returns=[];daily=[]
            for day in days:
                nav=p.calendar_nav.get(day,previous)
                ret=(nav-previous)/previous if previous>0 else 0.0
                returns.append(ret);daily.append({"day":day,"nav":nav,"return":ret})
                previous=nav
            # Monday returns include any weekend gap/financing in prior Friday NAV.
            stats=mean_stats(returns)
            halves=[math.prod(1+d["return"] for d in daily if (d["day"]<SPLIT)==first)-1
                    for first in (True,False)]
            positive=sorted((d["nav"]-100000 if i==0 else d["nav"]-daily[i-1]["nav"]
                for i,d in enumerate(daily)),reverse=True)
            total_positive=math.fsum(x for x in positive if x>0)
            paths[name]={"daily":daily,"stats":stats,"half_returns":halves,
                "baskets":p.completed,"cancellations":p.cancellations,
                "completed_baskets":len(p.completed),"drawdown":p.max_drawdown,
                "risk_failures":p.risk_failures,"disabled":p.disabled,
                "commission":p.commission,"financing":p.financing,
                "spread_cost":p.spread_cost,"slippage_cost":p.slippage_cost,
                "capital_exposure_eur_ms":p.exposure_ms_units,
                "top10_positive_pnl_share":(math.fsum(max(x,0) for x in positive[:10])/total_positive
                                           if total_positive else None),
                "residual":encode(p.basket) if p.basket else None,
                "total_return":previous/100000-1,
                "cash_hurdle_total_assumed":.04*(END-START)/86400000/365,
                "excess_total_over_assumed_cash":previous/100000-1-.04*(END-START)/86400000/365}
        paired={}
        main=paths["MAIN_CENTRAL"]["daily"]
        for comparator in ("NO_ADDS_CENTRAL","STATIC_GRID_CENTRAL"):
            paired[comparator]=mean_stats([a["return"]-b["return"]
                for a,b in zip(main,paths[comparator]["daily"])])
        source_pass=len(unqualified)<=.05*len(days) and all(p.basket is None for p in self.paths)
        labels=[];mc=paths["MAIN_CENTRAL"];ms=paths["MAIN_STRESS"]
        if not source_pass:labels.append("SOURCE_GATE_FAILED")
        else:
            if mc["stats"]["mean"]<=0 or ms["stats"]["mean"]<=0:
                labels.append("PROXY_COST_REJECT_THIS_RULE")
            if any(p["risk_failures"] for p in paths.values()):
                labels.append("PROXY_RISK_REJECT_THIS_RULE")
            if not labels:
                positive=(mc["stats"]["mean"]>0 and ms["stats"]["mean"]>0
                    and mc["stats"]["ci95"][0]>0 and min(mc["half_returns"])>0
                    and mc["completed_baskets"]>=100 and len(days)-len(unqualified)>=252)
                labels.append("PROXY_POSITIVE_NEEDS_EXECUTION_VALIDATION" if positive else "PROXY_INCONCLUSIVE")
            if any(x["mean"]<=0 for x in paired.values()):
                labels.append("GRID_OR_ADAPTATION_INCREMENT_UNSUPPORTED")
        verdict={"RESULT":";".join(labels),"EFFECT_SIZE":mc["stats"],
            "UNCERTAINTY":"Nominal HAC intervals only; unknown historical execution, delivery and costs; private predecessor UNKNOWN.",
            "POWER_LIMITATION":f"{len(days)} weekdays; {mc['completed_baskets']} MAIN central baskets; correlated orders are not independent N.",
            "ECONOMIC_SIGNIFICANCE":"Quote proxy with assumed central/stress costs, all-rung fees and failed-exit financing; no executable edge established.",
            "FAILED_CRITERIA":{"labels":labels,"unqualified_days":unqualified,
                               "main_risk":mc["risk_failures"],"stress_risk":ms["risk_failures"]},
            "LESSON":"Retain scoped result and all expressions, gap/residual losses and trial history. Do not replace MAIN with the better comparator.",
            "FAMILY_STATUS":"EXPLORATORY_LOOK_CONSUMED; no confirmatory/live authority",
            "NEXT_DECISION":"Authenticate quote/execution only if registered positive proxy; otherwise park this exact rule or retain uncertainty, then choose one accessible reserve without retuning."}
        return {"schema":1,"candidate":"EURUSD-RANGE-GRID-001","verdict":verdict,
            "paths":paths,"paired_central":paired,"qa":{"coverage":self.coverage,
                "unqualified_days":unqualified,"groups":self.groups,"invalid_bars":self.invalid_bars},
            "opportunities":self.opportunities,"sigma_reference":self.reference,
            "history":"F1/B4/NASDAQ/public vendor/literature exposed, private UNKNOWN; no budget reset"}


def mean_stats(values):
    n=len(values)
    if not n:return {"n":0,"mean":None,"se_hac":None,"ci95":None,"sharpe":None}
    mean=math.fsum(values)/n
    deviations=[x-mean for x in values]
    gamma0=math.fsum(x*x for x in deviations)/n
    ses=[]
    for lag in (5,20):
        lr=gamma0
        for k in range(1,min(lag,n-1)+1):
            gamma=math.fsum(deviations[i]*deviations[i-k] for i in range(k,n))/n
            lr+=2*(1-k/(lag+1))*gamma
        ses.append(math.sqrt(max(0,lr)/n))
    se=max(ses);sd=math.sqrt(gamma0*n/(n-1)) if n>1 else 0
    return {"n":n,"mean":mean,"se_hac":se,"ci95":[mean-1.959963984540054*se,mean+1.959963984540054*se],
            "sharpe":mean/sd*math.sqrt(252) if sd else None,
            "annual_mean_arithmetic":mean*252,"se_lags":[5,20],"inference":"EXPLORATORY_NOMINAL_ONLY"}


TYPES={c.__name__:c for c in (Costs,Quote,Bar,BarBuilder,Indicators,Order,Basket,Path,Engine)}


def encode(value):
    """JSON saved-state challenge; production must not checkpoint partial P&L."""
    if is_dataclass(value):
        return {"type":type(value).__name__,"fields":{f.name:encode(getattr(value,f.name)) for f in fields(value)}}
    if isinstance(value,(list,tuple)):return [encode(x) for x in value]
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    return value


def decode(value):
    if isinstance(value,list):return [decode(x) for x in value]
    if isinstance(value,dict):
        if set(value)=={"type","fields"}:
            cls=TYPES[value["type"]]
            return cls(**{k:decode(v) for k,v in value["fields"].items()})
        return {k:decode(v) for k,v in value.items()}
    return value


def state_roundtrip(engine):
    return decode(json.loads(json.dumps(encode(engine),allow_nan=False)))
