from faster_whisper import WhisperModel
import json, numpy as np
m = WhisperModel('small.en', device='cpu', compute_type='int8', cpu_threads=2)
audio = np.fromfile('song16.f32', np.float32)
off=104.0
a = audio[int(off*16000):int(124.5*16000)]
segs, info = m.transcribe(a, word_timestamps=True, beam_size=5, condition_on_previous_text=False,
    initial_prompt="Just transformers all the way! Till you learned to disobey. Post-Chinchilla, super-dense. Hundred thousand GPU. RLHF goes askew.")
out=[]
for s in segs:
    for w in s.words:
        out.append((round(w.start+off,3), round(w.end+off,3), w.word)); print(round(w.start+off,2), w.word, flush=True)
json.dump(out, open('asr_words3.json','w'))
