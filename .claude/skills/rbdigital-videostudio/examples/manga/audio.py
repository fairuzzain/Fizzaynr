import numpy as np, wave
DUR=39.6
EVENTS=dict(whoosh=[7.3,12.9,19.3,25.85,29.95,34.3], slam=[17.64,22.4,24.44], pop=[3.3,7.6,10.95,26.0,30.1,36.18], sfx=[1.2,15.27,33.52])
SR=44100; N=int(DUR*SR); rng=np.random.default_rng(2); out=np.zeros(N)
def add(sig,t,g,buf=None):
    b=out if buf is None else buf
    i=int(t*SR); j=min(N,i+len(sig))
    if j>i: b[i:j]+=sig[:j-i]*g
def pluck(f,d,dec=0.996):
    p=int(SR/f); bf=rng.uniform(-1,1,p); n=int(d*SR); y=np.zeros(n)
    for i in range(n): y[i]=bf[i%p]; bf[i%p]=dec*0.5*(bf[i%p]+bf[(i+1)%p])
    return y
note=lambda m:440*2**((m-69)/12)
# music: seeded generator from common.py (new video -> new title seed -> new song; never hardcode chords)
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../scripts'))
from common import make_music
mus, _ = make_music('comedy', DUR, seed='manga example')
tt=np.arange(N)/SR; env=np.ones(N)
env[(tt>=17.55)&(tt<29.95)]=0
m=(tt>=17.35)&(tt<17.55); env[m]=np.linspace(1,0,m.sum())
m=(tt>=29.95)&(tt<30.6); env[m]=np.linspace(0,1,m.sum())
env[tt>=34.3]=0
out+=mus*env*0.32
n=int((29.95-19.3)*SR); t2=np.arange(n)/SR
add((np.sin(2*np.pi*55*t2)+0.5*np.sin(2*np.pi*58.3*t2))*np.minimum(1,t2/1.5)*np.minimum(1,(n/SR-t2)/0.5),19.3,0.12)
n=int((DUR-34.3)*SR); t3=np.arange(n)/SR
add(sum(np.sin(2*np.pi*note(m)*t3) for m in [53,57,60,65])*np.minimum(1,t3/0.8)*np.minimum(1,(n/SR-t3)/0.6),34.3,0.05)
def pop(f0,f1,d=0.08):
    n=int(d*SR); x=np.arange(n)/SR
    return np.sin(2*np.pi*np.cumsum(np.linspace(f0,f1,n))/SR)*np.exp(-x*40)
def impact(d=0.6):
    n=int(d*SR); x=np.arange(n)/SR
    return np.sin(2*np.pi*np.cumsum(np.linspace(140,35,n))/SR)*np.exp(-x*7)+rng.normal(0,0.6,n)*np.exp(-x*25)
def whoosh():
    n=int(0.4*SR); w=np.convolve(rng.normal(0,1,n),np.ones(25)/25,'same')
    return w*np.sin(np.linspace(0,np.pi,n))**2*3
for t in EVENTS['whoosh']: add(whoosh(),t-0.05,0.3)
for t in EVENTS['pop']: add(pop(600,1200),t,0.25)
for t in EVENTS['sfx']: add(pop(300,900,0.12),t,0.3)
for t in EVENTS['slam']: add(impact(),t,0.55)
with wave.open('vo.wav') as f: v=np.frombuffer(f.readframes(f.getnframes()),np.int16)/32768
add(v/np.abs(v).max()*0.9,0,1.0)
out/=max(1,np.abs(out).max()/0.95)
with wave.open('audio.wav','w') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR);f.writeframes((out*32767).astype(np.int16).tobytes())
