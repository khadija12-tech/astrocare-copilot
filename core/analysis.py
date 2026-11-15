"""Personal baseline, drift detection (z-scores + Isolation Forest), system scores, explanations."""
import numpy as np, pandas as pd
from sklearn.ensemble import IsolationForest
from .config import SIGNALS, SYSTEMS, BASELINE_DAYS

BAD = pd.Series({s: v["bad"] for s, v in SIGNALS.items()})

TWO_SIDED = [s for s, v in SIGNALS.items() if v['bad'] == 0]

def harm(z):
    h = (z * BAD).clip(lower=0)
    for s in TWO_SIDED: h[s] = z[s].abs()
    return h

def system_scores(z):
    h = harm(z); out = pd.DataFrame(index=z.index)
    for sy in SYSTEMS:
        cols = [s for s, v in SIGNALS.items() if v["system"] == sy]
        out[sy] = (100 * np.exp(-h[cols].mean(axis=1) / 4)).round(1)
    return out

def overall(sc):
    return (0.5 * sc[SYSTEMS].min(axis=1) + 0.5 * sc[SYSTEMS].mean(axis=1)).round(1)

def baseline_stats(g):
    b = g[g.day < BASELINE_DAYS][list(SIGNALS)]
    return b.mean(), b.std().clip(lower=1e-3)

def detect_day(g):
    zc = g[["z_" + s for s in SIGNALS]].copy(); zc.columns = list(SIGNALS)
    n = (harm(zc) > 2.5).sum(axis=1)
    hit = (n >= 2) & (n.shift(1, fill_value=0) >= 2) & (g.day >= BASELINE_DAYS)
    return int(g.day[hit].iloc[0]) if hit.any() else None

def analyze(df):
    frames, stats, det = [], {}, {}
    for name, g in df.groupby("astronaut"):
        g = g.sort_values("day").reset_index(drop=True)
        mu, sd = baseline_stats(g); stats[name] = (mu, sd)
        z = (g[list(SIGNALS)].rolling(3, min_periods=1).mean() - mu) / sd
        sc = system_scores(z)
        for sy in SYSTEMS: g["score_" + sy] = sc[sy].values
        g["overall"] = overall(sc).values
        iso = IsolationForest(n_estimators=200, random_state=0).fit(z.values[:BASELINE_DAYS])
        ds = iso.decision_function(z.values)
        g["iso_score"] = -ds
        g["iso_flag"] = ds < (ds[:BASELINE_DAYS].min() - 0.02)
        for s in SIGNALS: g["z_" + s] = z[s].values
        det[name] = detect_day(g)
        frames.append(g)
    return pd.concat(frames, ignore_index=True), stats, det

def fmt_delta(s, m, mu):
    d = m - mu
    if s in ("temp", "glucose", "bp_sys"):
        return f"{d:+.1f} {SIGNALS[s]['unit']}" if s == "temp" else f"{d:+.0f} {SIGNALS[s]['unit']}"
    if s == "sleep_h":
        mins = int(round(abs(d) * 60)); return f"{'+' if d >= 0 else '-'}{mins // 60}h{mins % 60:02d}"
    if s in ("mood", "fatigue"):
        return f"{d:+.1f} pts"
    return f"{100 * d / mu:+.0f}%"

def explain(g, stats, day, window=5, min_harm=2.0):
    mu, sd = stats
    w = g[(g.day > day - window) & (g.day <= day)]
    items = []
    for s, meta in SIGNALS.items():
        m = w[s].mean(); dz = (m - mu[s]) / sd[s]; hz = abs(dz) if meta["bad"] == 0 else dz * meta["bad"]
        if hz >= min_harm:
            items.append(dict(signal=s, label=meta["label"], harm_z=round(float(hz), 1),
                              text=f"{meta['label']} {fmt_delta(s, m, mu[s])} vs baseline (last {window} days)"))
    return sorted(items, key=lambda x: -x["harm_z"])

def interpret(items):
    s = {i["signal"] for i in items}; out = []
    if ({"sleep_h", "fatigue"} & s) and ({"rhr", "hrv"} & s):
        out.append("Pattern consistent with accumulated fatigue and physiological stress.")
    if len({"mood", "voice_pitch_var", "speech_rate", "social_min"} & s) >= 2:
        out.append("Mood, voice and social signals are shifting together: possible psychological strain or withdrawal.")
    if "exercise_min" in s:
        out.append("Reduced exercise load raises the risk of muscle and bone deconditioning in microgravity.")
    if {"immune_idx", "sleep_h"} <= s:
        out.append("Short sleep with a raised immune stress marker: immune resilience may be reduced.")
    if "bp_sys" in s:
        out.append("Blood pressure is trending up: recheck at rest and review salt, sleep and exercise.")
    if "glucose" in s:
        out.append("Blood glucose is drifting from your baseline: review meals, activity and stress.")
    if "temp" in s:
        out.append("Raised temperature with immune and heart-rate changes: possible infection. Limit close contact and contact the flight surgeon." if {"immune_idx", "rhr"} & s
                   else "Body temperature differs from your baseline: measure again in a few hours.")
    if "radiation_dose" in s:
        out.append("Radiation dose rate is elevated: possible solar particle event. Follow shelter procedures and inform the ground team.")
    return out

def headline(scores, items):
    low = [k for k, v in scores.items() if v < 75]
    if not low: return "All systems within personal baseline."
    return ("Early warning: " + ", ".join(low) + " trending away from baseline.") if items else "Minor deviation, keep monitoring."
