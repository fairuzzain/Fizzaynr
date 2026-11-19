#!/usr/bin/env python3
"""toon_build.py plan.json -> final MP4 (shots + xfade + captions + lower-thirds + VO + music + SFX). Needs only ffmpeg + stdlib.
Runs ffmpeg inside workdir (relative subtitle path works on Windows). Optional plan keys: xfade, cap_font, cap_size, lt_font, lower_thirds.
Put .ttf files in <workdir>/fonts to make libass find them."""
import json, subprocess, sys, os
P=json.load(open(sys.argv[1],encoding="utf-8")); W=P["workdir"]; Wd,Ht=P.get("size",[1920,1080]); FPS=P.get("fps",24)
T=P.get("xfade",0.3); LEAD=0.15; sc=P["scenes"]; N=len(sc); TOTAL=P["total"]
def run(c): subprocess.run(c,check=True,cwd=W)
b=[0]+[s["start"]-LEAD for s in sc[1:]]+[TOTAL]
os.makedirs(f"{W}/seg",exist_ok=True)
for i,s in enumerate(sc):
    d=b[i+1]-b[i]+(T if i<N-1 else 0)
    shots=s.get("shots") or [{"from":0.1,"zoom":1.0}]
    sd=d/len(shots); parts=[]
    for k,sh in enumerate(shots):
        z=sh.get("zoom",1.0); cx=sh.get("cx",0.5); cy=sh.get("cy",0.5); spd=sh.get("speed",1.0)
        crop=f"crop=iw/{z}:ih/{z}:(iw-iw/{z})*{cx}:(ih-ih/{z})*{cy}," if z!=1.0 else ""
        out=f"{W}/seg/{i:02d}_{k}.mp4"
        run(["ffmpeg","-v","error","-y","-ss",str(sh.get("from",0.1)),"-i",f"{W}/{s['clip']}","-vf",
            f"setpts={1/spd:.4f}*PTS,{crop}scale={Wd}:{Ht}:flags=lanczos,fps={FPS},format=yuv420p,tpad=stop_mode=clone:stop_duration=3,trim=duration={sd:.3f},setpts=PTS-STARTPTS",
            "-an","-c:v","libx264","-crf","16","-preset","fast",out])
        parts.append(out)
    lst=f"{W}/seg/{i:02d}.txt"; open(lst,"w",encoding="utf-8").write("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",lst,"-c","copy",f"{W}/seg/{i:02d}.mp4"])
def ts(x): return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
fs=P.get("cap_size",58); mv=70 if Wd>Ht else 380
ass=f"[Script Info]\nScriptType: v4.00+\nPlayResX: {Wd}\nPlayResY: {Ht}\nWrapStyle: 0\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Cap,{P.get("cap_font","Poppins")},{fs},&H00FFFFFF,&H00FFFFFF,&H00202A3A,&H80000000,-1,0,0,0,100,100,0,0,1,5,2,2,{int(Wd*0.11)},{int(Wd*0.11)},{mv},1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
for s in sc:
    for c in s.get("captions",[{"text":s.get("text",""),"start":s["start"],"end":s["end"]}]):
        ass+=f"Dialogue: 0,{ts(c['start'])},{ts(min(c['end']+0.25,TOTAL-0.8))},Cap,,0,0,0,,{{\\fad(120,120)}}{c['text']}\n"
ass=ass.replace("\n\n[Events]",f"\nStyle: LT,{P.get('lt_font','Georgia')},50,&H00EEF4F8,&H00FFFFFF,&H00101010,&H00000000,-1,0,0,0,100,100,3,0,1,3,2,7,90,90,70,1\n\n[Events]")
for l in P.get("lower_thirds",[]):
    ass+=f"Dialogue: 1,{ts(l['start'])},{ts(l['end'])},LT,,0,0,0,,{{\\fad(400,400)}}{l['text']}\n"
open(f"{W}/caps.ass","w",encoding="utf-8").write(ass)
sfx=P.get("sfx",[]); bed=None
if sfx:
    inp=[];fc="";labs=[]
    for i,e in enumerate(sfx):
        inp+=(["-stream_loop","-1"] if e.get("loop") else [])+["-i",f"{W}/{e['file']}"]
        d=e["end"]-e["start"]+0.6; st=int(max(0,e["start"]-0.3)*1000)
        fc+=f"[{i}:a]aresample=44100,aformat=channel_layouts=stereo,atrim=duration={d:.2f},afade=t=in:d=0.4,afade=t=out:st={d-0.7:.2f}:d=0.7,volume={e.get('gain',1.0)},adelay={st}|{st}[s{i}];"; labs.append(f"[s{i}]")
    fc+="".join(labs)+f"amix=inputs={len(labs)}:normalize=0:duration=longest,atrim=duration={TOTAL}[o]"
    bed=f"{W}/sfx_bed.wav"; run(["ffmpeg","-v","error","-y"]+inp+["-filter_complex",fc,"-map","[o]",bed])
inp=[]
for i in range(N): inp+=["-i",f"{W}/seg/{i:02d}.mp4"]
FD=":fontsdir=fonts" if os.path.isdir(f"{W}/fonts") else ""
fc="";prev="[0:v]";off=0
for i in range(1,N):
    off+=b[i]-b[i-1]; fc+=f"{prev}[{i}:v]xfade=transition=fade:duration={T}:offset={off:.3f}[v{i}];"; prev=f"[v{i}]"
fc+=f"{prev}subtitles=caps.ass{FD},fade=t=in:st=0:d=0.5,fade=t=out:st={TOTAL-1.2}:d=1.2[vout];"
ai=N; inp+=["-i",f"{W}/{P['vo']}"]; mix=f"[{ai}:a]apad[vo];"; labs="[vo]"; n=1
if P.get("music"):
    inp+=["-i",f"{W}/{P['music']}"]; ai+=1; mix+=f"[{ai}:a]volume={P.get('music_gain',0.12)}[mu];"; labs+="[mu]"; n+=1
if bed:
    inp+=["-i",bed]; ai+=1; mix+=f"[{ai}:a]volume={P.get('sfx_gain',0.7)}[sx];"; labs+="[sx]"; n+=1
fc+=mix+f"{labs}amix=inputs={n}:normalize=0:duration=longest,atrim=duration={TOTAL},afade=t=out:st={TOTAL-1.5}:d=1.5,alimiter=limit=0.79:level=false[aout]"
run(["ffmpeg","-v","error","-y"]+inp+["-filter_complex",fc,"-map","[vout]","-map","[aout]","-c:v","libx264","-crf","18","-preset","medium","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-t",str(TOTAL),"-movflags","+faststart",f"{W}/{P['output']}"])
print("rendered",P["output"])
