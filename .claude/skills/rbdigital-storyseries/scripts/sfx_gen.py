#!/usr/bin/env python3
"""sfx_gen.py <preset> out.wav <seconds>  -> free procedural SFX made with ffmpeg only (no API, no numpy).
sfx_gen.py --list  -> show presets.
Good for beds and textures (wind, rain, room tone, city hum, film crackle, crickets) and simple hits
(boom, whoosh, chime, tick). Specific sounds (rooster, crowd cheering, a car) come from free libraries instead."""
import subprocess, sys

# each preset: (lavfi source, extra audio filter). D = duration in seconds.
P = {
 "wind":      ("anoisesrc=c=brown:a=0.5:d={D}", "lowpass=f=600,volume='0.55+0.45*sin(2*PI*0.13*t)*sin(2*PI*0.047*t+1)':eval=frame"),
 "rain":      ("anoisesrc=c=pink:a=0.4:d={D}", "highpass=f=500,lowpass=f=7000"),
 "room":      ("anoisesrc=c=brown:a=0.15:d={D}", "lowpass=f=220"),
 "city":      ("anoisesrc=c=brown:a=0.4:d={D}", "lowpass=f=350,volume='0.8+0.2*sin(2*PI*0.08*t)':eval=frame"),
 "crowd_far": ("anoisesrc=c=pink:a=0.35:d={D}", "bandpass=f=700:width_type=h:w=900,volume='0.6+0.25*sin(2*PI*0.7*t)*sin(2*PI*0.23*t)+0.15*sin(2*PI*1.9*t)':eval=frame"),
 "waves":     ("anoisesrc=c=brown:a=0.6:d={D}", "lowpass=f=900,volume='0.25+0.75*pow(sin(PI*t/7),2)':eval=frame"),
 "fire":      ("aevalsrc='0.25*(random(0)*2-1)*0.3+if(gt(random(1),0.9985),(random(2)*2-1)*0.9,0)':d={D}", "lowpass=f=3000,highpass=f=80"),
 "crackle":   ("aevalsrc='0.02*(random(0)*2-1)+if(gt(random(1),0.9994),(random(2)*2-1)*0.7,0)':d={D}", "highpass=f=300,lowpass=f=6000"),
 "projector": ("aevalsrc='0.03*(random(0)*2-1)+0.35*lt(mod(t*24,1),0.06)*(random(1)*2-1)+if(gt(random(2),0.9994),(random(3)*2-1)*0.5,0)':d={D}", "bandpass=f=1800:width_type=h:w=2500"),
 "crickets":  ("aevalsrc='0.25*sin(2*PI*4400*t)*gt(sin(2*PI*28*t),0)*lt(mod(t,1.3),0.35)+0.15*sin(2*PI*5100*t)*gt(sin(2*PI*31*t),0)*lt(mod(t+0.6,1.7),0.3)':d={D}", "lowpass=f=8000"),
 "tick":      ("aevalsrc='0.6*lt(mod(t,1),0.004)*sin(2*PI*2500*t)':d={D}", "aecho=0.6:0.3:30:0.3"),
 "heartbeat": ("aevalsrc='0.9*sin(2*PI*55*t)*(exp(-mod(t,0.9)*25)+0.7*exp(-abs(mod(t,0.9)-0.22)*30)*gte(mod(t,0.9),0.22))':d={D}", "lowpass=f=200"),
 "boom":      ("aevalsrc='0.9*sin(2*PI*(38+50*exp(-t*6))*t)*exp(-t*1.6)+0.2*(random(0)*2-1)*exp(-t*12)':d={D}", "lowpass=f=400,aecho=0.8:0.6:180|420:0.35|0.2"),
 "whoosh":    ("anoisesrc=c=pink:a=0.6:d={D}", "highpass=f=300,lowpass=f=5000,volume='pow(sin(PI*t/{D}),3)':eval=frame"),
 "chime":     ("aevalsrc='(0.5*sin(2*PI*1046.5*t)+0.3*sin(2*PI*2093*t)+0.15*sin(2*PI*3139.5*t)+0.3*sin(2*PI*1318.5*max(t-0.12,0))*gte(t,0.12))*exp(-t*2.2)':d={D}", "aecho=0.7:0.5:90:0.3"),
 "drone":     ("aevalsrc='0.3*sin(2*PI*73.42*t)*(0.7+0.3*sin(2*PI*0.05*t))+0.15*sin(2*PI*110*t)+0.06*sin(2*PI*146.83*t)*(0.5+0.5*sin(2*PI*0.03*t))':d={D}", "lowpass=f=900,aecho=0.8:0.7:120|260:0.3|0.2"),
}

if len(sys.argv) < 2 or sys.argv[1] == "--list":
    print("presets:", ", ".join(P)); sys.exit(0)
name, out, d = sys.argv[1], sys.argv[2], float(sys.argv[3])
if name not in P:
    sys.exit(f"unknown preset {name}; choose from: {', '.join(P)}")
src, flt = P[name]; D = f"{d:.2f}"
fade = f"afade=t=in:d={min(0.3, d/4):.2f},afade=t=out:st={max(0, d-min(0.6, d/3)):.2f}:d={min(0.6, d/3):.2f}"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", src.format(D=D),
                "-af", f"{flt.format(D=D)},{fade},aformat=channel_layouts=stereo", "-ar", "44100", "-t", D, out], check=True)
print("wrote", out)
