import json, re, difflib
from lyrics import LINES
A=json.load(open('asr_words.json')); B=json.load(open('asr_words3.json')); C=json.load(open('asr_words2.json'))
asr=[w for w in A if w[0]<103.9]+[w for w in B if w[0]<123.7]+[w for w in C if w[0]>=123.7]
def nz(s): return re.sub(r'[^a-z0-9]','',s.lower())
toks=[(a,b,nz(s)) for a,b,s in asr if nz(s) and not nz(s).startswith('ooo')]
lw=[]
for li,(t0,t1,txt) in enumerate(LINES):
    for w in txt.split(): lw.append((li,w,nz(w)))
n,m=len(lw),len(toks)
import math
def sim(a,b):
    if not a or not b: return 0
    return difflib.SequenceMatcher(None,a,b).ratio()
INF=1e9
D=[[INF]*(m+1) for _ in range(n+1)];P=[[None]*(m+1) for _ in range(n+1)]
D[0]=[0.0]*(m+1)  # allow skipping leading asr
for i in range(n+1):
    for j in range(m+1):
        if D[i][j]>=INF: continue
        if i<n and j<m:
            s=sim(lw[i][2],toks[j][2]); c=D[i][j]+(1-s)*2
            if c<D[i+1][j+1]: D[i+1][j+1]=c;P[i+1][j+1]=(i,j,'M')
        if i<n:
            c=D[i][j]+1.2
            if c<D[i+1][j]: D[i+1][j]=c;P[i+1][j]=(i,j,'L')
        if j<m:
            c=D[i][j]+0.9
            if c<D[i][j+1]: D[i][j+1]=c;P[i][j+1]=(i,j,'A')
j=min(range(m+1),key=lambda j:D[n][j]); i=n
match={}
while i>0:
    pi,pj,op=P[i][j]
    if op=='M' and sim(lw[pi][2],toks[pj][2])>0.34: match[pi]=pj
    i,j=pi,pj
out=[]
for k,(li,w,z) in enumerate(lw):
    out.append([li,w,toks[match[k]][0] if k in match else None, toks[match[k]][1] if k in match else None])
# interpolate gaps
for k in range(len(out)):
    if out[k][2] is None:
        a=k-1
        while a>=0 and out[a][2] is None: a-=1
        b=k+1
        while b<len(out) and out[b][2] is None: b+=1
        ta=out[a][3] if a>=0 else 0.0; tb=out[b][2] if b<len(out) else 141.0
        out[k][2]=ta+(tb-ta)*(k-a)/(b-a); out[k][3]=None
json.dump(out,open('word_times.json','w'))
cur=-1
for li,w,s,e in out:
    if li!=cur: print(); print(f"{li:2d} {LINES[li][0]:7.2f}|",end=' '); cur=li
    print(f"{w}@{s:.2f}{'' if e else '*'}",end=' ')
print()
