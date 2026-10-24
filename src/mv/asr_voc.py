from faster_whisper import WhisperModel
import json, numpy as np
v=np.fromfile('vocals44.f32',np.float32)
# resample 44.1k -> 16k (linear)
n=int(len(v)*16000/44100)
a=np.interp(np.arange(n)*44100/16000, np.arange(len(v)), v).astype(np.float32)
a=a/ (np.abs(a).max()+1e-9)*0.9
m=WhisperModel('small.en', device='cpu', compute_type='int8', cpu_threads=2)
segs,_=m.transcribe(a, word_timestamps=True, beam_size=5, condition_on_previous_text=False, vad_filter=False)
out=[]
for s in segs:
    for w in s.words:
        out.append((round(w.start,3), round(w.end,3), w.word))
json.dump(out, open('asr_voc.json','w')); print(len(out))
