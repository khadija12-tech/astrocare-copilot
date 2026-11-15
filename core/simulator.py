"""Simulated crew data (Amira: fatigue/stress drift, Jonas: withdrawal, Mateo: short fever, all: day-49 solar event). Ranges are plausible, NOT measured - always label as simulated."""
import numpy as np, pandas as pd
from .config import SIGNALS

CREW = ["Amira", "Jonas", "Keiko", "Mateo"]
NOISE = dict(rhr=1.2, hrv=3, sleep_h=.3, sleep_eff=.02, immune_idx=.04, exercise_min=8,
             mood=.4, fatigue=.5, voice_pitch_var=.25, speech_rate=.15, social_min=15, radiation_dose=.04, bp_sys=3, glucose=4, temp=.12)
MEAN = dict(rhr=(62, 3), hrv=(65, 6), sleep_h=(7.2, .3), sleep_eff=(.9, .02), immune_idx=(1.0, .05),
            exercise_min=(120, 8), mood=(7.5, .4), fatigue=(3, .5), voice_pitch_var=(2.8, .2),
            speech_rate=(4.2, .2), social_min=(180, 15), radiation_dose=(.6, .03), bp_sys=(118, 5), glucose=(90, 5), temp=(36.6, .1))

def _ramp(d, start, length):
    return float(np.clip((d - start) / length, 0, 1))

def simulate(days=60, seed=23):
    """Amira: fatigue/stress drift from day 35. Jonas: social withdrawal from day 42."""
    rng = np.random.default_rng(seed)
    rows = []
    for name in CREW:
        b = {s: rng.normal(*MEAN[s]) for s in SIGNALS}
        for d in range(days):
            r = _ramp(d, 35, 20) if name == "Amira" else 0.0
            j = _ramp(d, 42, 15) if name == "Jonas" else 0.0
            v = {s: b[s] + rng.normal(0, NOISE[s]) for s in SIGNALS}
            v["rhr"] += b["rhr"] * .12 * r
            v["hrv"] -= b["hrv"] * .25 * r
            v["sleep_h"] -= 1.5 * r
            v["sleep_eff"] -= .08 * r
            v["immune_idx"] += .25 * r
            v["exercise_min"] -= 35 * r
            v["mood"] -= 2.5 * r + 1.2 * j
            v["fatigue"] += 3 * r
            v["voice_pitch_var"] -= 1.4 * r + .8 * j
            v["speech_rate"] -= .6 * r
            v["social_min"] -= 60 * r + 90 * j
            v["bp_sys"] += 14 * r; v["glucose"] += 10 * r
            f = {52: .5, 53: .9, 54: .9, 55: .5}.get(d, 0) if name == "Mateo" else 0   # scripted fever episode
            v["temp"] += 1.0 * f; v["immune_idx"] += .2 * f; v["rhr"] += 6 * f
            v["radiation_dose"] += {48: .5, 49: .9, 50: .5}.get(d, 0)   # simulated solar particle event, whole crew
            v["sleep_eff"] = min(v["sleep_eff"], 1.0)
            v["mood"] = float(np.clip(v["mood"], 0, 10)); v["fatigue"] = float(np.clip(v["fatigue"], 0, 10))
            rows.append({"day": d, "astronaut": name, **{k: round(max(x, 0), 3) for k, x in v.items()}})
    return pd.DataFrame(rows)

def simulate_interactions(df, seed=11):
    """Pairwise daily contact minutes + sentiment. Amira-Jonas tension from day 45."""
    rng = np.random.default_rng(seed)
    soc = df.pivot(index="day", columns="astronaut", values="social_min")
    mood = df.pivot(index="day", columns="astronaut", values="mood")
    names = list(soc.columns); rows = []
    for d in soc.index:
        for i in range(len(names)):
            for k in range(i + 1, len(names)):
                a, b = names[i], names[k]
                minutes = max(0.0, 40 * (soc.loc[d, a] + soc.loc[d, b]) / 360 + rng.normal(0, 4))
                conflict = _ramp(d, 45, 10) * .7 if {a, b} == {"Amira", "Jonas"} else 0.0
                sent = .6 + .03 * (mood.loc[d, a] + mood.loc[d, b] - 15) + rng.normal(0, .06) - conflict
                rows.append(dict(day=int(d), a=a, b=b, minutes=round(minutes, 1), sentiment=float(np.clip(sent, -1, 1))))
    return pd.DataFrame(rows)
