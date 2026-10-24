import numpy as np, torch
from demucs.pretrained import get_model
from demucs.apply import apply_model
torch.set_num_threads(4)
m=get_model('htdemucs'); m.eval()
a=np.fromfile('song44.f32',np.float32).reshape(-1,2).T.copy()
w=torch.from_numpy(a)
ref=w.mean(0); w=(w-ref.mean())/ref.std()
with torch.no_grad():
    s=apply_model(m,w[None],device='cpu',split=True,overlap=0.1,progress=False)[0]
s=s*ref.std()+ref.mean()
v=s[m.sources.index('vocals')].mean(0).numpy().astype(np.float32)
v.tofile('vocals44.f32'); print('done',v.shape)
