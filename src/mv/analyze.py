import numpy as np, json
sr=22050; x=np.fromfile('song.f32',dtype=np.float32)
dur=len(x)/sr
hop=256; n=1024
frames=(len(x)-n)//hop
idx=np.arange(n)[None,:]+hop*np.arange(frames)[:,None]
S=np.abs(np.fft.rfft(x[idx]*np.hanning(n),axis=1))
freqs=np.fft.rfftfreq(n,1/sr)
t=np.arange(frames)*hop/sr+n/2/sr
logS=np.log1p(10*S)
flux=np.maximum(0,np.diff(logS,axis=0)).sum(1); flux=np.r_[0,flux]
low=S[:,(freqs>30)&(freqs<150)].sum(1)
lowflux=np.maximum(0,np.diff(np.log1p(low)));lowflux=np.r_[0,lowflux]
hi=S[:,(freqs>5000)].sum(1)
rms=np.sqrt((x[idx]**2).mean(1))
# tempo search
fr=sr/hop
o=flux-np.convolve(flux,np.ones(32)/32,'same'); o=np.maximum(o,0)
best=None
for bpm in np.arange(120,145,0.05):
    period=60/bpm*fr
    for ph in np.linspace(0,period,48,endpoint=False):
        pos=(ph+np.arange(0,frames,period)).astype(int); pos=pos[pos<frames]
        sc=o[pos].mean()
        if best is None or sc>best[0]: best=(sc,bpm,ph/fr)
print('tempo',best,'dur',dur)
json.dump({'dur':dur,'bpm':best[1],'phase':best[2]},open('tempo.json','w'))
# per-video-frame features at 30fps
FPS=30; N=int(np.ceil(dur*FPS))
vt=np.arange(N)/FPS
def res(a):
    return np.interp(vt,t,a)
def norm(a):
    a=a/ (np.percentile(a,99)+1e-9); return np.clip(a,0,1.5)
feat={'rms':norm(res(rms)),'low':norm(res(low)),'hi':norm(res(hi)),'flux':norm(res(o)),'lowflux':norm(res(lowflux))}
np.savez('feat.npz',**feat)
# print section energy every 2s
for s in range(0,int(dur),2):
    print(s, round(float(feat['rms'][s*FPS:(s+2)*FPS].mean()),2), round(float(feat['low'][s*FPS:(s+2)*FPS].mean()),2))
