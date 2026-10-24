import numpy as np, json
v=np.fromfile('vocals44.f32',np.float32); sr=44100; hop=441
n=len(v)//hop
e=np.sqrt((v[:n*hop].reshape(n,hop)**2).mean(1))+1e-9
db=20*np.log10(e/e.max())
sm=np.convolve(db,np.ones(3)/3,'same')
np.save('vocdb.npy',sm)
TH=-30
def on(t): return sm[int(t*100)] > TH
wt=json.load(open('word_times.json'))
print('frac active', (sm>TH).mean())
# print per line first word: active state and first active frame
prev=None
for i,(li,w,s,e_) in enumerate(wt):
    gap = (prev is None) or (prev[0]!=li)
    if gap:
        k=int(s*100)
        seg=sm[k:k+150]
        idx=np.argmax(seg>TH) if (seg>TH).any() else -1
        print(li,w,round(s,2),'act' if on(s) else 'SILENT','-> onset',round(s+idx/100,2) if idx>=0 else None)
    prev=(li,w,s,e_)
