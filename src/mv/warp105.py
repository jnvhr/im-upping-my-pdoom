"""v109: back to the original 132 BPM. Identity warp (output time == song time).
Old variants: warp105_v107.py (142 ramp), warp105_v108_136.py (uniform 136)."""
PEAK = 132.0


def bpm_at(t):
    return 132.0


def tau(t):
    return t


def src(T):
    return T
