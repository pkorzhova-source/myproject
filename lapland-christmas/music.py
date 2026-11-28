# Music-box arrangement of "Jingle Bells" (public domain) with sleigh bells and a warm pad, 20 s.
import numpy as np, wave
sr = 44100; D = 20.0; t = np.arange(int(sr * D)) / sr
out = np.zeros((len(t), 2))
beat = 0.6; t0 = 0.5
N = {'G4': 392.0, 'A4': 440.0, 'B4': 493.88, 'C5': 523.25, 'D5': 587.33, 'E5': 659.25}
mel = [('B4',1),('B4',1),('B4',2), ('B4',1),('B4',1),('B4',2), ('B4',1),('D5',1),('G4',1.5),('A4',.5), ('B4',4),
       ('C5',1),('C5',1),('C5',1.5),('C5',.5), ('C5',1),('B4',1),('B4',1),('B4',.5),('B4',.5), ('D5',1),('D5',1),('C5',1),('A4',1), ('G4',4)]
chords = [['G3','B3','D4'],['G3','B3','D4'],['G3','B3','D4'],['G3','B3','D4'],['C3','E3','G3'],['G3','B3','D4'],['D3','F#3','A3','C4'],['G3','B3','D4']]
F = {'C3':130.81,'E3':164.81,'G3':196.0,'D3':146.83,'F#3':185.0,'A3':220.0,'B3':246.94,'C4':261.63,'D4':293.66}

def add(sig, start, pan=0.0):
    i = int(start * sr); n = min(len(sig), len(t) - i)
    if n <= 0: return
    out[i:i+n, 0] += sig[:n] * (1 - pan) ; out[i:i+n, 1] += sig[:n] * (1 + pan)

def bell(f, dur=2.5, amp=1.0):
    tt = np.arange(int(sr * dur)) / sr
    s = (np.sin(2*np.pi*f*tt) * np.exp(-tt*2.2) + 0.45*np.sin(2*np.pi*f*2*tt) * np.exp(-tt*3.5)
         + 0.25*np.sin(2*np.pi*f*3.01*tt) * np.exp(-tt*6) + 0.12*np.sin(2*np.pi*f*5.4*tt) * np.exp(-tt*9))
    return amp * s * np.minimum(1, tt / 0.004)

# melody, an octave up, with a soft echo
pos = t0
for n, d in mel:
    add(bell(N[n]*2, amp=0.55), pos, -0.15)
    add(bell(N[n]*2, amp=0.16), pos + 0.3, 0.35)
    pos += d * beat
# pad chords
for i, ch in enumerate(chords):
    st = t0 + i * 4 * beat; dur = 4 * beat + 0.6
    tt = np.arange(int(sr * dur)) / sr
    env = np.minimum(1, tt / 0.5) * np.minimum(1, (dur - tt) / 0.6)
    s = sum(np.sin(2*np.pi*F[c]*tt) + 0.3*np.sin(2*np.pi*F[c]*2.003*tt) for c in ch) / len(ch)
    add(0.16 * s * env, st)
    # plucked bass on beats 1 and 3
    root = F[ch[0]] / 2
    for b in (0, 2):
        bt = np.arange(int(sr * 1.2)) / sr
        add(0.22 * np.sin(2*np.pi*root*bt) * np.exp(-bt*3) * np.minimum(1, bt/0.01), st + b * beat)
# sleigh bells on eighth notes
rng = np.random.default_rng(7)
for k in range(int((19.2 - t0) / (beat / 2))):
    st = t0 + k * beat / 2
    bt = np.arange(int(sr * 0.25)) / sr
    nz = rng.standard_normal(len(bt))
    nz = np.diff(np.concatenate([[0], nz]))  # crude high-pass
    jing = sum(np.sin(2*np.pi*f*bt) for f in (5200, 6300, 7400, 8800)) * 0.25
    s = (0.5 * nz + jing) * np.exp(-bt * (18 if k % 2 else 11)) * (1.0 if k % 2 == 0 else 0.6)
    add(0.05 * s, st, 0.25 * np.sin(k))
# gentle ending chime
add(bell(N['G4']*4, 4, 0.35), t0 + 32 * beat + 0.05, 0.2)

# room-ish reverb via a few delays
rev = out.copy()
for dl, g in ((0.043, 0.35), (0.067, 0.3), (0.11, 0.25), (0.17, 0.18), (0.23, 0.12)):
    n = int(dl * sr); rev[n:] += out[:-n][:, ::-1] * g
out = rev
env = np.minimum(1, t / 0.4) * np.minimum(1, (D - t) / 1.2)
out *= env[:, None]
out = out / np.abs(out).max() * 0.85
w = wave.open('music.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()
print('ok')
