import numpy as np, wave
SR=44100; DUR=41.6; N=int(DUR*SR); rng=np.random.default_rng(9); out=np.zeros(N); tt=np.arange(N)/SR
def add(sig,t,g):
    i=int(t*SR); j=min(N,i+len(sig))
    if j>i: out[i:j]+=sig[:j-i]*g
def lp(x,k): return np.convolve(x,np.ones(k)/k,'same')
# drone + wind bed
drone=np.sin(2*np.pi*48*tt)+0.6*np.sin(2*np.pi*48.7*tt)+0.3*np.sin(2*np.pi*72.3*tt+np.sin(tt*0.7)*2)
wind=lp(rng.normal(0,1,N),60)*(0.6+0.4*np.sin(tt*0.5))
bed=(drone*0.09+wind*0.5)
env=np.clip(tt/2,0,1)*np.clip((40.0-tt)/0.6,0,1)
env*=1+0.8*((tt>26.5)&(tt<32.3))
out+=bed*env*0.6
def shutter():
    n=int(0.12*SR); x=np.arange(n)/SR
    c=rng.normal(0,1,n)*np.exp(-x*120); c2=np.zeros(n); k=int(0.05*SR); c2[k:]=rng.normal(0,1,n-k)*np.exp(-(x[k:]-0.05)*90)
    return c+0.8*c2
def paper():
    n=int(0.2*SR); x=np.arange(n)/SR; return lp(rng.normal(0,1,n),4)*np.exp(-x*18)
def knock():
    n=int(0.3*SR); x=np.arange(n)/SR
    return np.sin(2*np.pi*95*x)*np.exp(-x*22)+lp(rng.normal(0,1,n),8)*np.exp(-x*60)*0.6
def boom(d=2.5):
    n=int(d*SR); x=np.arange(n)/SR
    b=np.sin(2*np.pi*np.cumsum(np.linspace(70,28,n))/SR)*np.exp(-x*1.6)
    s=np.sin(2*np.pi*(1800+300*np.sin(x*40))*x)*np.exp(-x*3)*0.12
    return b+s+lp(rng.normal(0,1,n),3)*np.exp(-x*6)*0.3
def heart(t0,t1,bpm=70):
    t=t0
    while t<t1:
        for dt,g in [(0,1),(0.18,0.7)]:
            n=int(0.15*SR); x=np.arange(n)/SR; add(np.sin(2*np.pi*50*x)*np.exp(-x*30),t+dt,0.5*g)
        t+=60/bpm; bpm+=4
def static(d):
    n=int(d*SR); return rng.normal(0,1,n)*(rng.random(n)>0.3)
for t in [0.25,7.2,11.45,13.6,19.28,22.78,28.1,35.64]: add(shutter(),t,0.35)
for t in [2.0,9.5,15.1,21.85,30.66]: add(paper(),t,0.2)
for t in [17.62,17.9,18.9]: add(knock(),t,0.7)
heart(26.5,32.2)
for t in [20.45,29.25,37.8]: add(boom(),t,0.5)
for t,d in [(20.45,0.35),(21.85,0.2),(29.25,0.5),(31.2,0.15),(37.8,0.4),(38.8,0.25),(39.4,0.3),(40.2,0.25)]: add(static(d),t,0.12)
with wave.open('vo.wav') as f: v=np.frombuffer(f.readframes(f.getnframes()),np.int16)/32768
add(v/np.abs(v).max()*0.9,0,1.0)
out/=max(1,np.abs(out).max()/0.95)
with wave.open('audio.wav','w') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(SR);f.writeframes((out*32767).astype(np.int16).tobytes())
