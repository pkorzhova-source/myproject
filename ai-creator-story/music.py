import numpy as np, wave
sr=44100; D=15; t=np.arange(sr*D)/sr
chords=[[220.0,277.2,329.6],[185.0,233.1,277.2],[146.8,185.0,220.0],[164.8,207.7,246.9]]
sig=np.zeros_like(t)
for i in range(8):
    f=chords[i%4]; a=i*2; m=(t>=a)&(t<a+2.6); lt=t[m]-a
    env=np.minimum(1,lt/0.6)*np.exp(-lt*0.6)
    for fr in f: sig[m]+=env*(np.sin(2*np.pi*fr*t[m])+0.2*np.sin(2*np.pi*fr*2.005*t[m]))
pulse=np.zeros_like(t)
for k in np.arange(0,D,0.25):
    m=(t>=k)&(t<k+0.12); lt=t[m]-k
    pulse[m]+=np.sin(2*np.pi*880*lt)*np.exp(-lt*40)
s=sig/3+0.08*pulse
s*=np.minimum(1,t/0.8)*np.minimum(1,(D-t)/1.0)
s=(s/np.abs(s).max()*0.9*32767).astype(np.int16)
w=wave.open('music.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(s.tobytes()); w.close()
