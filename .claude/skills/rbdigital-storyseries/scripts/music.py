#!/usr/bin/env python3
"""music.py out.wav seconds -> soft placeholder music bed (numpy only).
Edit the drone/scale/beat lines to fit the style (comments show the cheerful variant)."""
import numpy as np, wave, sys
sr=44100; dur=float(sys.argv[2]); n=int(sr*dur); t=np.arange(n)/sr
out=np.zeros(n)
for f,a in [(73.42,.18),(110,.10),(146.83,.06)]:  # drone; cheerful: (130.81,.10),(196.0,.06),(261.63,.04)
    out+=a*np.sin(2*np.pi*f*t+0.3*np.sin(2*np.pi*0.1*t))
scale=[293.66,311.13,369.99,392.0,440.0,466.16,523.25,587.33]  # Middle East; cheerful: [523.25,587.33,659.25,783.99,880.0,1046.5,1174.66,1318.5]
pat=[0,2,4,3,2,1,0,4,5,4,3,2,4,2,1,0]; beat=0.6; k=0; s=0.0  # cheerful: beat=0.42
while s<dur-1:
    f=scale[pat[k%len(pat)]]; k+=1; i0=int(s*sr); L=min(int(1.6*sr),n-i0); x=np.arange(L)/sr
    tone=np.sin(2*np.pi*f*x)+0.4*np.sin(2*np.pi*2*f*x)+0.15*np.sin(2*np.pi*3*f*x)
    out[i0:i0+L]+=0.10*tone*np.minimum(1,x/0.005)*np.exp(-x/0.35); s+=beat*(2 if k%8==0 else 1)
s=0.0
while s<dur-0.5:
    i0=int(s*sr); L=int(0.4*sr); x=np.arange(L)/sr
    out[i0:i0+L]+=0.22*np.sin(2*np.pi*(90*np.exp(-x*8)+55)*x)*np.exp(-x*9); s+=beat*2
out*=np.minimum(1,np.minimum(t/2,(dur-t)/3)); out/=np.max(np.abs(out))*1.1
d=(out*32767).astype(np.int16); d=np.stack([d,d],1)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(d.tobytes()); w.close()
