"""v93: splice via per-segment inputs (base segments input-seeked) so ffmpeg never buffers the whole base video.
Edit SEG for new chunks. Usage: python3 splice_seg.py out_name.mp4"""
import sys, subprocess
B = 'pdoom_v59_web.mp4'
SEG = [(B, 0, 392), 'out4/v60/c0392_v87.mp4', (B, 502, 796), 'out4/v60/c0796_v86.mp4', (B, 904, 1030),
       'out4/v60/c1030_v63.mp4', (B, 1160, 1594), 'out4/v60/c1594_v87.mp4', (B, 1774, 1920), 'out4/v60/c1920_v66.mp4',
       (B, 2000, 2090), ('out4/v60/c2090_v67.mp4', 134), 'out4/v60/c2224_v68.mp4', (B, 2334, 2394),
       ('out4/v60/c2394_v69.mp4', 43), 'out4/v60/c2437_v83.mp4', 'out4/v60/c2680_v87.mp4', (B, 2858, 2906),
       ('out4/v60/c2906_v89.mp4', 54), 'out4/v60/c2960_v96.mp4', ('out4/v60/c3075_v94.mp4', 229), ('out4/v60/c3304_v96.mp4', 151), 'out4/v60/c3455_v98.mp4', (B, 3515, 4120),
       'out4/v60/c4120_v90.mp4', (B, 4210, 4701)]
import os
os.makedirs('/tmp/seg', exist_ok=True)
ENC = ['-c:v', 'libx264', '-crf', '20', '-maxrate', '8M', '-bufsize', '16M', '-preset', 'veryfast', '-pix_fmt', 'yuv420p',
       '-r', '30', '-an', '-threads', '4']
lst = []
for i, s in enumerate(SEG):
    o = '/tmp/seg/%02d.mp4' % i
    if isinstance(s, tuple) and len(s) == 3:
        src, vf = s[0], 'select=between(n\\,%d\\,%d),setpts=N/30/TB' % (s[1], s[2] - 1)
    elif isinstance(s, tuple):
        src, vf = s[0], 'select=lt(n\\,%d),setpts=N/30/TB' % s[1]
    else:
        src, vf = s, 'setpts=N/30/TB'
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-threads', '2', '-i', src, '-vf', vf] + ENC + [o], check=True)
    lst.append("file '%s'" % o)
open('/tmp/seg/list.txt', 'w').write('\n'.join(lst) + '\n')
subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', '/tmp/seg/list.txt', '-i', 'song.mp3',
                '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart',
                '/tmp/' + sys.argv[1]], check=True)
subprocess.run(['cp', '/tmp/' + sys.argv[1], sys.argv[1]], check=True)
subprocess.run('rm -rf /tmp/seg /tmp/' + sys.argv[1], shell=True)
