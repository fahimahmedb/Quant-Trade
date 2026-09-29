import requests, json, time
RPCS=["https://polygon-bor-rpc.publicnode.com","https://polygon.drpc.org"]
TRANSFER="0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
def call(method, params, tries=4):
    last=None
    for i in range(tries):
        rpc=RPCS[i%len(RPCS)]
        try:
            r=requests.post(rpc,json={"jsonrpc":"2.0","id":1,"method":method,"params":params},timeout=60)
            j=r.json()
            if "result" in j: return j["result"]
            last=j
        except Exception as e:
            last=str(e)
        time.sleep(1+i)
    raise RuntimeError(f"{method} failed: {last}")
def erc20_meta(tok):
    def s(sel):
        r=call("eth_call",[{"to":tok,"data":sel},"latest"])
        return r
    name=s("0x06fdde03"); sym=s("0x95d89b41"); dec=int(s("0x313ce567"),16)
    def dec_str(h):
        b=bytes.fromhex(h[2:])
        if len(b)>=96:
            ln=int.from_bytes(b[32:64],'big'); return b[64:64+ln].decode(errors='replace')
        return b.rstrip(b'\0').decode(errors='replace')
    return dec_str(name),dec_str(sym),dec
import datetime
def block_ts(n): return int(call("eth_getBlockByNumber",[hex(n),False])["timestamp"],16)
def block_at(ts, lo=None, hi=None):
    hi=hi or int(call("eth_blockNumber",[]),16)
    lo=lo or hi-20_000_000
    while hi-lo>1:
        mid=(lo+hi)//2
        if block_ts(mid)<ts: lo=mid
        else: hi=mid
    return hi
def logs_range(address, topics, b0, b1, step=9999):
    out=[]; b=b0
    while b<=b1:
        e=min(b+step,b1)
        out+=call("eth_getLogs",[{"address":address,"topics":topics,"fromBlock":hex(b),"toBlock":hex(e)}])
        b=e+1
    return out
PUSD="0xc011a7e12a19f7b1f670d46f03b03f3342e82dfb"
REWARD_DIST="0xdd8db71ce3be8d71ff148b2163d64da181a29e8b"
REBATE_EOA="0xfdb1b8dc7f5789a0c9a398026585b8b10fba5507"
def pad(a): return "0x"+"0"*24+a[2:].lower()
