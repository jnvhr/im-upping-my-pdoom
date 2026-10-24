"""v3 blocky mouth (box teeth, tube lips), restored from the v3 bytecode in jaw_v3.pyc (source was lost)."""
import marshal, types, os
_m = None


def s_jaw_v3(g, t, lt):
    global _m
    if _m is None:
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'jaw_v3.pyc')
        code = marshal.loads(open(p, 'rb').read()[16:])
        _m = types.ModuleType('s4a_v3'); _m.__file__ = p
        exec(code, _m.__dict__)
    return _m.s_jaw(g, t, lt)
