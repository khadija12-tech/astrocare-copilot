"""Export simulated analysis to vr/data.js and mobile/data.js (run: python export_web.py)."""
import json
from core import simulator, analysis as an
from core.config import SYSTEMS, SYSTEM_LABEL

df = simulator.simulate(); A, stats, det = an.analyze(df); crew = {}
for name, g in A.groupby("astronaut"):
    g = g.sort_values("day"); last = int(g.day.max())
    items = an.explain(g, stats[name], last); sc = {s: float(g.iloc[-1]["score_" + s]) for s in SYSTEMS}
    crew[name] = {"scores": [[round(float(r["score_" + s])) for s in SYSTEMS] for _, r in g.iterrows()],
                  "overall": [round(float(x)) for x in g.overall], "detected": det[name],
                  "headline": an.headline(sc, items), "drivers": [i["text"] for i in items[:4]]}
data = {"days": int(A.day.max()) + 1, "systems": SYSTEMS, "labels": [SYSTEM_LABEL[s] for s in SYSTEMS], "delay": 20, "crew": crew}
js = "window.ASTRO=" + json.dumps(data, separators=(",", ":")) + ";"
for d in ("vr", "mobile"):
    open(f"{d}/data.js", "w").write(js)
print("exported", len(js), "bytes")
