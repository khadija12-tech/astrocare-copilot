"""Crew dynamics: pairwise sentiment/contact drift and individual isolation."""
import numpy as np, pandas as pd
from .config import BASELINE_DAYS

def pair_summary(inter, day, window=5):
    base = inter[inter.day < BASELINE_DAYS].groupby(["a", "b"]).sentiment.mean().rename("baseline")
    rec = inter[(inter.day > day - window) & (inter.day <= day)].groupby(["a", "b"]).agg(
        sentiment=("sentiment", "mean"), minutes=("minutes", "mean")).join(base)
    rec["delta"] = rec.sentiment - rec.baseline
    rec["status"] = np.where(rec.delta < -.3, "tension", np.where(rec.delta < -.15, "watch", "ok"))
    return rec.reset_index().round(2)

def isolation_table(A, stats, day, window=5):
    rows = []
    for name, g in A.groupby("astronaut"):
        mu, _ = stats[name]
        m = g[(g.day > day - window) & (g.day <= day)].social_min.mean()
        pct = 100 * (m - mu["social_min"]) / mu["social_min"]
        rows.append(dict(astronaut=name, social_min=round(m), vs_baseline_pct=round(pct),
                         status="isolated" if pct < -25 else "watch" if pct < -12 else "ok"))
    return pd.DataFrame(rows)
