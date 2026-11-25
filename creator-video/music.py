import numpy as np, wave
sr=44100; D=20; t=np.arange(sr*D)/sr
chords=[[261.6,329.6,392.0],[220.0,261.6,329.6],[174.6,220.0,261.6],[196.0,246.9,293.7]]
sig=np.zeros_like(t)
for i in range(10):  # 2s per chord
    f=chords[i%4]; m=(t>=i*2)&(t<i*2+2.05); lt=t[m]-i*2
    env=np.minimum(1,lt/0.08)*np.exp(-lt*0.9)
    for fr in f: sig[m]+=env*(np.sin(2*np.pi*fr*t[m])+0.3*np.sin(4*np.pi*fr*t[m]))
beat=np.zeros_like(t)
for k in np.arange(0,D,0.5):  # soft kick
    m=(t>=k)&(t<k+0.25); lt=t[m]-k
    beat[m]+=np.sin(2*np.pi*(55+90*np.exp(-lt*30))*lt)*np.exp(-lt*14)
s=0.18*sig/3+0.5*beat
s*=np.minimum(1,t/0.5)*np.minimum(1,(D-t)/1.2)
s=(s/np.abs(s).max()*0.8*32767).astype(np.int16)
w=wave.open('music.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(s.tobytes()); w.close()
