from faster_whisper import WhisperModel
import json
m = WhisperModel('small.en', device='cpu', compute_type='int8', cpu_threads=2)
import numpy as np
audio = np.fromfile('song16.f32', np.float32)
segs, info = m.transcribe(audio, word_timestamps=True, vad_filter=False, beam_size=5,
    initial_prompt="I see sparks of AGI in your eyes. ChatGPT, please don't eat me alive. I'm upping my P(doom). Shoggoth, shinigami, Sydney, basilisk, NVDA, Omega Point, von Neumann, CDR, Gato, paperclips, killswitch, PTO, orthogonality, Chinchilla, RLHF, Ilya.")
out = []
for s in segs:
    for w in s.words:
        out.append((round(w.start, 3), round(w.end, 3), w.word))
        print(round(w.start, 2), round(w.end, 2), w.word, flush=True)
json.dump(out, open('asr_words.json', 'w'))
