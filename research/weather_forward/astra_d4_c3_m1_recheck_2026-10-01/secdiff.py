import re, hashlib
def secs(path):
    out = {}; cur = 'HEADER'; buf = []
    for line in open(path, encoding='utf-8'):
        m = re.match(r'^(#{2,3}) (\d+(\.\d+[a-z]?)?)\b', line)
        if m:
            out[cur] = ''.join(buf); cur = m.group(2); buf = []
        buf.append(line)
    out[cur] = ''.join(buf)
    return out
o, n = secs('spec_old.md'), secs('spec_new.md')
keys = list(dict.fromkeys(list(o) + list(n)))
same, diff = [], []
for k in keys:
    (same if o.get(k) == n.get(k) else diff).append(k)
print('IDENTICAL:', ' '.join(same))
print('CHANGED/NEW:', ' '.join(diff))
for k in ('3','5.2','8.5','9','10.2','14','15','8.1','8.4','8.5b','17.2','17.5','17.6','10.1','11.4','6.3'):
    print(k, 'identical' if o.get(k) == n.get(k) else 'CHANGED')
