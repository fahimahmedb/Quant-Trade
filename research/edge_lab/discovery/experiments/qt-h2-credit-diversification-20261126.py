#!/usr/bin/env python3
"""Frozen exploratory credit allocation protocol #7180737247. No orders."""
import math,statistics as st,random,json,hashlib,urllib.request,re,sys
from html.parser import HTMLParser
URL="https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/histretSP.html"
class Rows(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.rows=[];self.row=None;self.cell=None
    def close_cell(self):
        if self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()));self.cell=None
    def close_row(self):
        if self.row is not None:
            self.close_cell()
            if self.row:self.rows.append(self.row)
            self.row=None
    def handle_starttag(self,t,a):
        if t=="tr":self.close_row();self.row=[]
        elif t in ("td","th") and self.row is not None:self.close_cell();self.cell=[]
        elif t=="br" and self.cell is not None:self.cell.append(" ")
    def handle_endtag(self,t):
        if t in ("td","th"):self.close_cell()
        elif t=="tr":self.close_row()
    def handle_data(self,d):
        if self.cell is not None:self.cell.append(d)
def norm(x):return re.sub(r"[^a-z0-9]","",x.lower())
def parse(s,first=1928,last=2025):
    h=Rows();h.feed(s);h.close_row()
    expected=["year","sp500includesdividends","ussmallcapbottomdecile","3monthtbill","ustbond10year","baacorporatebond"]
    heads=[i for i,r in enumerate(h.rows) if list(map(norm,r[:6]))==expected]
    if len(heads)!=1:raise ValueError("header not uniquely identified")
    out=[]
    for row in h.rows[heads[0]+1:]:
        if not row or not re.fullmatch(r"\d{4}",row[0]):continue
        y=int(row[0])
        if not first<=y<=last:continue
        vals=[]
        for i in (1,3,4,5):
            if not re.fullmatch(r"[-+]?\d+(?:\.\d+)?%",row[i]):raise ValueError("percentage schema")
            v=float(row[i][:-1])/100
            if not math.isfinite(v) or not -1<v<5:raise ValueError("return outside bounds")
            vals.append(v)
        out.append((y,*vals))
    if [x[0] for x in out]!=list(range(first,last+1)):raise ValueError("coverage/order/duplicates")
    print("QA "+json.dumps(dict(rows=len(out),first=first,last=last,header=h.rows[heads[0]][:6])),flush=True)
    return out
def acquire():
    with urllib.request.urlopen(urllib.request.Request(URL,headers={"User-Agent":"QuantTrade bounded academic research"}),timeout=25) as r:
        if not r.url.startswith("https://pages.stern.nyu.edu/"):raise ValueError("unexpected redirect")
        b=r.read(4000001);encoding=r.headers.get_content_charset() or "windows-1252"
    if len(b)>4000000:raise ValueError("oversize")
    print("SOURCE "+json.dumps(dict(url=URL,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b))),flush=True)
    return parse(b.decode(encoding,errors="strict"))
def path(rows,w,fee,extra):
    c=fee/10000;held=[0.,0.,0.];out=[]
    for i,(y,e,rf,t,b) in enumerate(rows):
        turn=sum(abs(a-z) for a,z in zip(held,w))
        gross_assets=[(1+e)*.998,(1+t)*.998,(1+b)*.998*(1-extra)]
        g=sum(a*z for a,z in zip(w,gross_assets));f=g*(1-c*turn)
        held=[a*z/g for a,z in zip(w,gross_assets)]
        if i==len(rows)-1:f*=1-c*sum(held);turn+=sum(held)
        out.append((y,f,turn))
    return out
def metrics(z):
    log=peak=0.;dd=0.
    for _,g,_ in z:log+=math.log(g);peak=max(peak,log);dd=min(dd,math.exp(log-peak)-1)
    return dict(n=len(z),wealth=math.exp(log),cagr=math.expm1(log/len(z)),vol=st.stdev(g-1 for _,g,_ in z),dd=dd,worst=min(g-1 for _,g,_ in z),annual_turnover=st.mean(t for _,_,t in z))
def paired(a,b):
    assert [x[0] for x in a]==[x[0] for x in b]
    return [math.log(x[1]/y[1]) for x,y in zip(a,b)]
def boot(d):
    rng=random.Random(20261126);n=len(d);v=[]
    for _ in range(20000):
        s=0.
        for k in range(0,n,5):
            j=rng.randrange(n);s+=sum(d[(j+h)%n] for h in range(min(5,n-k)))
        v.append(s/n)
    v.sort();return v[249]
def evaluate(rows):
    train=[x for x in rows if x[0]<=1969];test=[x for x in rows if x[0]>=1970]
    assert len(train)==42 and len(test)==56
    B=(.6,.4,0.);out={}
    ref=[(i/1000,1-i/1000,0.) for i in range(1001)]
    vols=[metrics(path(train,w,10,.0015))["vol"] for w in ref]
    for name,w in [("C20",(.6,.2,.2)),("C40",(.6,0.,.4))]:
        v=metrics(path(train,w,10,.0015))["vol"]
        k=min(range(len(ref)),key=lambda i:(abs(vols[i]-v),i));R=ref[k]
        modes={}
        for fee,extra in [(10,.0015),(30,.005)]:
            z={a:path(test,b,fee,extra) for a,b in [("C",w),("B",B),("R",R)]}
            s={k:metrics(v) for k,v in z.items()}
            db=paired(z["C"],z["B"]);dr=paired(z["C"],z["R"])
            phase={str(lo):st.mean(d for d,row in zip(dr,test) if lo<=row[0]<=hi) for lo,hi in [(1970,1989),(1990,2009),(2010,2025)]}
            a,b,r=s["C"],s["B"],s["R"]
            checks={"cagrB":a["cagr"]-b["cagr"]>=.0025,"cagrR":a["cagr"]-r["cagr"]>=.0025,"volB":a["vol"]<=b["vol"],"volR":a["vol"]<=r["vol"],"dd":a["dd"]>=b["dd"]-.02,"phase":all(x>0 for x in phase.values())}
            lower={}
            if fee==10:
                lower={"B":boot(db),"R":boot(dr)}
                checks.update(statB=lower["B"]>.0025,statR=lower["R"]>.0025)
            modes[str(fee)]=dict(stats=s,delta_log_B=st.mean(db),delta_log_R=st.mean(dr),phase=phase,lower=lower,checks=checks,screen=all(checks.values()))
        out[name]=dict(train_vol_C=v,train_vol_R=vols[k],risk_weight=R[0],modes=modes,screen=all(m["screen"] for m in modes.values()))
    descriptive=path(test,(0.,0.,1.),10,.0015)
    treas=path(test,(0.,1.,0.),10,.0015)
    return dict(candidates=out,pure_baa=metrics(descriptive),pure_treas=metrics(treas),mean_nominal_difference=st.mean(x[4]-x[3] for x in test))
def selftest():
    h="<table><tr><td>Year</td><td>S&P 500 (includes dividends)</td><td>US Small cap (bottom decile)</td><td>3-month T.Bill</td><td>US T. Bond (10-year)</td><td>Baa Corporate Bond</td></tr><tr><td>1928</td><td>10.00%</td><td>12.00%</td><td>2.00%</td><td>-5.00%</td><td>4.00%</td></tr></table>"
    assert parse(h,1928,1928)==[(1928,.1,.02,-.05,.04)]
    x=path([(1928,.1,.02,-.05,.04)],(.6,.4,0.),10,.0015)
    assert abs(x[0][1]-.999**2*.998*(.6*1.1+.4*.95))<1e-12
    assert abs(boot([.01]*56)-.01)<1e-12
    print("SELF_TEST_PASS exact headers, calendar, fee timing, block bootstrap",flush=True)
if __name__=="__main__":
    if "--self-test" in sys.argv:selftest();sys.exit(0)
    try:
        out=evaluate(acquire());print("CREDIT_RESULT "+json.dumps(out,allow_nan=False,separators=(",",":")),flush=True)
    except Exception as e:
        print("BLOCK_DATA "+type(e).__name__+": "+str(e),flush=True);sys.exit(2)
