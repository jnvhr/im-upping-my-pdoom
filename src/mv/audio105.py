import numpy as np, soundfile as sf, subprocess, pytsmod
import warp105 as W
subprocess.run(['ffmpeg','-v','error','-y','-i','song.mp3','-f','wav','/tmp/song.wav'],check=True)
x, sr = sf.read('/tmp/song.wav', dtype='float32')
PAD = 0.4
a0, b0 = W.WA - PAD, W.WB + PAD
seg = x[int(round(a0*sr)):int(round(b0*sr))].T
# anchor points: input sample -> output sample (relative to segment start, which maps to itself)
ts = np.linspace(a0, b0, 400)
anc_in = np.round((ts - a0) * sr).astype(int)
anc_out = np.round((np.array([W.tau(t) for t in ts]) - a0) * sr).astype(int)
s = np.vstack([anc_in, anc_out])
y = np.vstack([pytsmod.hptsm(seg[c], s) for c in range(seg.shape[0])]).T.astype('float32')
L_out = anc_out[-1]
y = y[:L_out] if len(y) >= L_out else np.vstack([y, np.zeros((L_out-len(y), 2), 'float32')])
pre = x[:int(round(a0*sr))]
post = x[int(round(b0*sr)):]
# crossfade 25 ms at both joins against the original (aligned since pads are identity-mapped)
F = int(0.025*sr)
ramp = np.linspace(0,1,F,dtype='float32')[:,None]
i0 = int(round(a0*sr))
orig_head = x[i0:i0+F]
y[:F] = orig_head*(1-ramp) + y[:F]*ramp
orig_tail = x[int(round(b0*sr))-F:int(round(b0*sr))]
y[-F:] = y[-F:]*(1-ramp) + orig_tail*ramp
out = np.vstack([pre, y, post])
sf.write('song_v105.wav', out, sr)
print(len(x)/sr, len(out)/sr, (len(x)-len(out))/sr)
