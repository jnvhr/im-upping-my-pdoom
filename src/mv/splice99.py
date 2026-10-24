import subprocess, os
B='pdoom_v98_web.mp4'
SEG=[(B,0,3455),'c3455_v99.mp4',(B,3515,4701)]
os.makedirs('/tmp/seg',exist_ok=True)
ENC=['-c:v','libx264','-crf','20','-maxrate','8M','-bufsize','16M','-preset','veryfast','-pix_fmt','yuv420p','-r','30','-an','-threads','4']
lst=[]
for i,s in enumerate(SEG):
    o='/tmp/seg/%02d.mp4'%i
    if isinstance(s,tuple):
        src,vf=s[0],'select=between(n\\,%d\\,%d),setpts=N/30/TB'%(s[1],s[2]-1)
    else: src,vf=s,'setpts=N/30/TB'
    subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-threads','2','-i',src,'-vf',vf]+ENC+[o],check=True)
    lst.append("file '%s'"%o)
open('/tmp/seg/list.txt','w').write('\n'.join(lst)+'\n')
subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-f','concat','-safe','0','-i','/tmp/seg/list.txt','-i','song.mp3','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart','pdoom_v99_web.mp4'],check=True)
