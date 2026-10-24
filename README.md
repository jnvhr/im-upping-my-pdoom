# I'm Upping My P(doom)

A lyric music video for the song "P(doom)", rendered frame by frame from Python
code. No stock footage, downloaded images or traced references: every frame is
a pure function of song time.

Directed by **jnvhr**, built with Hark.

- **Journey site:** `site/` is a visual devlog of every iteration, from the
  first render (v1, 2026-10-07) to the v132 production master
  (1920x1080, 60 fps, 9,402 frames). Deployed on Cloudflare Pages.
- **Source:** `src/mv/` is the render engine and all scenes.
- **Changelog:** `src/mv/HISTORY.md`.

## Rendering

```bash
pip install numpy scipy aggdraw pillow soundfile
cd src/mv
# put the song next to the code as song.mp3 (not included in this repo)
python3 render4.py still 42.0 87.5        # preview stills -> st4/
python3 render4.py range 0 300 out.mp4    # render frames 0-299
PDOOM_FPS=60 python3 render4.py range 0 600 out60.mp4   # 60 fps
```

Fonts are read from `src/fonts/`. Timing data (`word_times.json`,
`tempo.json`: 132 BPM) and the small analysis caches are included. The song
audio and the audio-derived raw files (`*.f32`) are not, so mux the audio back
in with ffmpeg after rendering.

## Layout

| Path | What |
|---|---|
| `src/mv/render4.py` | entry point: stills and frame ranges |
| `src/mv/core.py`, `kit.py`, `cam3d.py` | drawing core, HUD, 3D camera |
| `src/mv/s4a.py`, `s4b.py`, `s4c.py` | scene timeline (TL list in `s4c.py`) |
| `src/mv/ov*.py`, `vault124.py`, `rec124b.py`, `show111.py`, ... | scene overrides |
| `src/mv/lyrics.py`, `trans4.py` | lyric timing and card transitions |

## License

Code and site: MIT (see `LICENSE`). Fonts: SIL OFL 1.1. Song: not included.
