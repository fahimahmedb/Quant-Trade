exec(open('t.py').read().split("PO=['PSH'")[0])
PO=['PSH','PSD','PSA']; PC=['PSCH','PSCD','PSCA']
res=[]
for meth in ['mult','power']:
  po=fair(PO,meth); pc=fair(PC,meth)
  for pref,fo,cl,lab in [('Max',po,pc,'MaxOpen/PinOpen'),('B365',po,pc,'B365Open/PinOpen'),('MaxC',pc,None,'MaxClose/PinClose'),('B365C',pc,None,'B365C/PinClose')]:
    P=np.stack([num(pref+o) for o in 'HDA'],1); e=P*fo-1
    for X,cap in [(0.02,100),(0.02,4),(0.05,4)]:
      m=(e>X)&np.isfinite(e)&(P<cap); r=np.where(win==1,P-1,-1)[m]
      # cluster by match: sum returns per match
      mm=np.where(m.any(1))[0]; rm=np.where(win==1,P-1,-1); rm=np.where(m,rm,0).sum(1)[mm]
      tcl=rm.mean()/rm.std()*np.sqrt(len(rm))*len(rm)/m.sum()
      s=dict(dev=meth,test=lab,X=X,cap=cap,n=int(m.sum()),ROI=round(100*r.mean(),2),t=round(r.mean()/r.std()*np.sqrt(len(r)),2),t_clu=round(tcl,2))
      if cl is not None: s['CLV']=round(100*np.nanmean((P*cl-1)[m]),2)
      res.append(s)
print(pd.DataFrame(res).to_string())
# by league for MaxClose power X=.02 cap 4
pc=fair(PC,'power'); P=np.stack([num('MaxC'+o) for o in 'HDA'],1); e=P*pc-1; m=(e>0.02)&(P<4)&np.isfinite(e)
r=np.where(win==1,P-1,-1); L=np.repeat(np.asarray(d.Div,dtype=object)[:,None],3,1)
print(pd.Series(r[m]).groupby(L[m]).agg(['size','mean']).round(3).T.to_string())
S=np.repeat(np.asarray(d.season,dtype=object)[:,None],3,1)
print(pd.Series(r[m]).groupby(S[m]).agg(['size','mean']).round(3).T.to_string())
po=fair(PO,'power');P=np.stack([num('Max'+o) for o in 'HDA'],1); e=P*po-1; m=(e>0.02)&(P<4)&np.isfinite(e); r=np.where(win==1,P-1,-1)
print('MaxOpen power cap4 by season');print(pd.Series(r[m]).groupby(S[m]).agg(['size','mean']).round(3).T.to_string())
# fraction of Max edges where B365/Pinnacle itself supplies price? how often Max > all named books
named=[c for c in ['B365','BW','IW','PS','WH','VC','BF','1XB','LB'] ]
NB=np.nanmax(np.stack([np.stack([num(b+o) for o in 'HDA'],1) for b in named]),0)
print('share of Max-open bets where Max > best named major book:', np.mean((P>NB+1e-9)[m]))
Pn=NB; e2=Pn*po-1; m2=(e2>0.02)&(Pn<4)&np.isfinite(e2); r2=np.where(win==1,Pn-1,-1)[m2]
print('best-of-named-books open power cap4 X2: n',m2.sum(),'ROI',100*r2.mean(),'t',r2.mean()/r2.std()*np.sqrt(len(r2)))
