"""Sound design: voice track + synthesized SFX (whoosh, pop) + an optional / synthesized music bed."""
import subprocess

import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000


def read_wav(path):
    raw = subprocess.check_output(["ffmpeg", "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"])
    return np.frombuffer(raw, np.float32).copy()


# Makes TTS sound more like a real mic recording: low-cut, warmth, presence, gentle compression,
# a very short room reflection and a touch of saturation. Pass "voice_fx": null in the episode to disable.
VOICE_FX = ("highpass=f=70,lowpass=f=15000,"
            "equalizer=f=180:t=q:w=1.0:g=2.5,equalizer=f=3200:t=q:w=1.2:g=3,equalizer=f=7500:t=q:w=2:g=-2,"
            "acompressor=threshold=-20dB:ratio=3.5:attack=4:release=90:makeup=3,"
            "aecho=0.9:0.6:18|31:0.10|0.06,asoftclip=type=tanh:threshold=0.9")


def process_voice(x, fx=VOICE_FX):
    if not fx:
        return x
    out = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                          "-af", fx, "-f", "f32le", "-ar", str(SR), "-ac", "1", "-"],
                         input=x.astype(np.float32).tobytes(), capture_output=True, check=True).stdout
    y = np.frombuffer(out, np.float32).copy()
    return y[: len(x)] if len(y) >= len(x) else np.pad(y, (0, len(x) - len(y)))


def whoosh(dur=0.7, seed=0):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    noise = rng.standard_normal(n).astype(np.float32)
    t = np.linspace(0, 1, n)
    out = np.zeros(n, np.float32)
    # sweep a band-pass up then down by blending a few fixed filters (cheap & smooth enough)
    centers = [300, 600, 1200, 2400, 4000]
    pos = np.sin(np.pi * t) * (len(centers) - 1)
    for i, c in enumerate(centers):
        sos = butter(2, [c * 0.7, min(c * 1.4, SR / 2 - 100)], btype="band", fs=SR, output="sos")
        band = sosfilt(sos, noise)
        w = np.clip(1 - np.abs(pos - i), 0, 1)
        out += band * w
    env = np.sin(np.pi * t) ** 2
    out *= env
    return out / (np.abs(out).max() + 1e-6) * 0.35


def pop(dur=0.12):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 900 * np.exp(-t * 18) + 380
    ph = 2 * np.pi * np.cumsum(f) / SR
    env = np.exp(-t * 38) * np.clip(t * 900, 0, 1)
    return (np.sin(ph) * env * 0.45).astype(np.float32)


def music_bed(duration, bpm=100, seed=1):
    """Light, unobtrusive synth bed (pad chords + soft kick/hat). Replace with a licensed track for uploads."""
    n = int(duration * SR)
    t = np.arange(n) / SR
    beat = 60 / bpm
    out = np.zeros(n, np.float32)
    # chord progression (Hz): Am - F - C - G, 2 bars each
    prog = [[220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [130.8, 196.0, 261.6], [196.0, 246.9, 293.7]]
    bar = 4 * beat
    for i in range(int(duration / (2 * bar)) + 1):
        chord = prog[i % 4]
        s, e = int(i * 2 * bar * SR), min(n, int((i + 1) * 2 * bar * SR))
        if s >= n:
            break
        tt = t[s:e] - t[s]
        env = np.clip(tt / 0.4, 0, 1) * np.clip((2 * bar - tt) / 0.4, 0, 1)
        for fr in chord:
            out[s:e] += 0.05 * env * (np.sin(2 * np.pi * fr * tt) + 0.3 * np.sin(2 * np.pi * fr * 2.003 * tt))
    # kick on every beat, hat on off-beats
    rng = np.random.default_rng(seed)
    k_n = int(0.25 * SR)
    kt = np.arange(k_n) / SR
    kick = np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-kt * 30)) / SR) * np.exp(-kt * 14) * 0.35
    hat = rng.standard_normal(int(0.05 * SR)) * np.exp(-np.arange(int(0.05 * SR)) / SR * 90) * 0.05
    hat = sosfilt(butter(2, 7000, btype="high", fs=SR, output="sos"), hat)
    nb = int(duration / beat)
    for b in range(nb):
        s = int(b * beat * SR)
        out[s:s + k_n] += kick[: max(0, min(k_n, n - s))]
        h = int((b + 0.5) * beat * SR)
        out[h:h + len(hat)] += hat[: max(0, min(len(hat), n - h))]
    fade = np.clip(t / 1.0, 0, 1) * np.clip((duration - t) / 1.5, 0, 1)
    return out * fade


def mix(duration, voice_clips, sfx, music=None, music_gain_db=-20, out_path="mix.wav", voice_fx=VOICE_FX):
    """voice_clips: [(t, samples)], sfx: [(t, samples)], music: samples or None. Voice ducks the music."""
    n = int(duration * SR) + SR
    voice = np.zeros(n, np.float32)
    for t, x in voice_clips:
        s = int(t * SR)
        voice[s:s + len(x)] += x[: n - s]
    voice = process_voice(voice, voice_fx)
    fx = np.zeros(n, np.float32)
    for t, x in sfx:
        s = max(0, int(t * SR))
        fx[s:s + len(x)] += x[: n - s]
    total = voice + fx * 0.6
    if music is not None:
        m = np.zeros(n, np.float32)
        m[: min(n, len(music))] = music[:n]
        # side-chain style ducking from the voice envelope
        env = np.abs(voice)
        k = int(0.25 * SR)
        env = np.convolve(env, np.ones(k) / k, mode="same")
        duck = 1.0 - 0.5 * np.clip(env / (env.max() * 0.3 + 1e-6), 0, 1)
        total += m * (10 ** (music_gain_db / 20)) * 3 * duck
    total /= max(1.0, np.abs(total).max() / 0.95)
    total = total[: int(duration * SR)]
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", str(SR), out_path],
                   input=total.astype(np.float32).tobytes(), check=True)
    return out_path
