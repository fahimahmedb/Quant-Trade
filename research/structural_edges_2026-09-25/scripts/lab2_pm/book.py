import json, pandas as pd, numpy as np
D='/tmp/claude-0/-home-user-Quant-Trade/d2846cea-5e9b-54a8-9c49-75ba0ab48fd0/scratchpad/pm/marketlenstrade_polymarket-historical-data/'
def replay(path, K=5):
    """Yield per-row top-K book state (after applying row). Returns DataFrame rows at each event time."""
    f=pd.read_parquet(path)
    bids={}; asks={}; out=[]; trades=[]
    for r in f.itertuples(index=False):
        et=r.event_type
        if et=='snapshot':
            bids={float(x['price']):float(x['size']) for x in json.loads(r.bids)} if isinstance(r.bids,str) else {}
            asks={float(x['price']):float(x['size']) for x in json.loads(r.asks)} if isinstance(r.asks,str) else {}
        elif et=='delta':
            book=bids if r.side=='BUY' else asks
            if r.size==0: book.pop(r.price,None)
            else: book[r.price]=r.size
        elif et=='trade':
            trades.append((r.t,r.price,r.size,r.side))
        bk=sorted(bids.items(),reverse=True)[:K]; ak=sorted(asks.items())[:K]
        out.append((r.t,et,bk,ak))
    return out,trades
