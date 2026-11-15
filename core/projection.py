"""30-day digital twin: damped trend vs. recovery if recommendations are followed (illustrative)."""
import numpy as np, pandas as pd
from .config import SIGNALS, SYSTEMS
from .analysis import system_scores, overall

def _clip(raw):
    raw = raw.clip(lower=0)
    raw["sleep_eff"] = raw["sleep_eff"].clip(upper=1)
    for c in ("mood", "fatigue"): raw[c] = raw[c].clip(upper=10)
    return raw

def project(g, mu, sd, horizon=30, recovery=0.05, damp=0.93):
    recent = g.tail(14); cur = g[list(SIGNALS)].tail(3).mean(); last = int(g.day.max())
    slopes = {}
    for s in SIGNALS:
        sl = np.polyfit(recent.day, recent[s], 1)[0]
        slopes[s] = sl if abs(sl * 14) / sd[s] > 1.5 else 0.0   # only extrapolate significant trends
    out = []
    for scen in ("No change", "Follow plan"):
        rows = []
        for k in range(horizon + 1):
            if scen == "No change":
                f = sum(damp ** i for i in range(1, k + 1))
                rows.append({s: cur[s] + slopes[s] * f for s in SIGNALS})
            else:
                rows.append({s: mu[s] + (cur[s] - mu[s]) * np.exp(-recovery * k) for s in SIGNALS})
        raw = _clip(pd.DataFrame(rows)); sc = system_scores((raw - mu) / sd)
        sc["overall"] = overall(sc); sc["day"] = last + np.arange(horizon + 1); sc["scenario"] = scen
        out.append(sc)
    return pd.concat(out, ignore_index=True)
