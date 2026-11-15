"""Offline voice-stress features with numpy only: pitch variability, speech rate, pause ratio.
Raw audio is never stored; only these numbers are kept."""
import io, wave
import numpy as np

SR = 16000

def read_wav(b):
    with wave.open(io.BytesIO(b)) as w:
        sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if sw != 2: raise ValueError("Please use 16-bit PCM WAV")
    x = np.frombuffer(raw, dtype=np.int16).astype(float) / 32768
    if ch > 1: x = x.reshape(-1, ch).mean(axis=1)
    if sr > SR:
        k = int(sr / SR); x = np.convolve(x, np.ones(k) / k, "same")
    if sr != SR:
        x = np.interp(np.arange(int(len(x) * SR / sr)) / SR, np.arange(len(x)) / sr, x)
    return x

def analyze(x, sr=SR):
    n, h = int(.04 * sr), int(.01 * sr); lo, hi = int(sr / 400), int(sr / 70)
    win = np.hanning(n); f0, en = [], []
    for i in range(0, len(x) - n, h):
        f = x[i:i + n] * win; en.append(np.sqrt(np.mean(f * f)))
        ac = np.fft.irfft(np.abs(np.fft.rfft(f, 2 * n)) ** 2)[:n]
        if ac[0] <= 0: f0.append(np.nan); continue
        p = lo + int(np.argmax(ac[lo:hi])); f0.append(sr / p if ac[p] / ac[0] > .5 else np.nan)
    en, f0 = np.array(en), np.array(f0)
    if len(en) < 50 or en.max() == 0: raise ValueError("Recording too short or silent")
    f0 = np.where(en > .15 * en.max(), f0, np.nan); v = f0[~np.isnan(f0)]
    pitch_var = float(np.std(12 * np.log2(v / v.mean()))) if len(v) > 10 else float("nan")
    sm = np.convolve(en, np.ones(5) / 5, "same"); thr = .3 * sm.max()
    peaks = [i for i in range(1, len(sm) - 1) if sm[i] > thr and sm[i] >= sm[i - 1] and sm[i] > sm[i + 1]]
    kept = []
    for p in peaks:
        if not kept or p - kept[-1] >= 12: kept.append(p)
    phrase = np.convolve(en, np.ones(25) / 25, "same") > .1 * en.max()
    speech_s = phrase.sum() * .01
    return dict(pitch_var=pitch_var, speech_rate=len(kept) / speech_s if speech_s > 0 else float("nan"),
                pause_ratio=float(1 - phrase.mean()), mean_f0=float(v.mean()) if len(v) else float("nan"),
                f0=f0, t=np.arange(len(f0)) * .01)

def synth_voice(kind="normal", dur=10.0, seed=0):
    """Synthetic demo voice. 'tired' = flatter pitch, slower rate, longer pauses."""
    rng = np.random.default_rng(seed); t = np.arange(int(SR * dur)) / SR
    rate, depth, pause = (4.2, 3.5, .25) if kind == "normal" else (3.6, 1.4, .7)
    contour = depth * np.sin(2 * np.pi * .6 * t) + .5 * depth * np.sin(2 * np.pi * 1.7 * t + 1)
    ph = 2 * np.pi * np.cumsum(150 * 2 ** (contour / 12)) / SR
    sig = np.sin(ph) + .5 * np.sin(2 * ph) + .25 * np.sin(3 * ph)
    syl = (.5 * (1 + np.sin(2 * np.pi * rate * t))) ** 1.2
    period = 2.0 + pause
    gate = np.convolve(((t % period) < 2.0).astype(float), np.ones(400) / 400, "same")
    x = sig * syl * gate
    return x / np.abs(x).max() * .6 + rng.normal(0, .003, len(t))

def to_wav_bytes(x):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    return buf.getvalue()
