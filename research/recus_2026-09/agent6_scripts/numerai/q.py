import requests,json,sys,time
URL='https://api-tournament.numer.ai/'
def q(query, variables=None):
    r=requests.post(URL,json={'query':query,'variables':variables or {}},timeout=60)
    try: return r.json()
    except Exception: return {'status':r.status_code,'text':r.text[:500]}
if __name__=='__main__':
    print(json.dumps(q(sys.argv[1]),indent=1)[:int(sys.argv[2]) if len(sys.argv)>2 else 5000])
