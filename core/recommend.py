"""Rule-based recommendations, re-ranked by crew feedback. Decision support, not diagnosis."""
from .config import SYSTEMS

CATALOG = {
 "metabolic": [("glucose_meal", "Review meals and glucose", "Log meals for 3 days, keep a fast sugar source within reach, and repeat the glucose check tomorrow under the same conditions. Tell the ground nutrition team if it stays off.", 2)],
 "cardio": [("bp_recheck", "Recheck blood pressure", "Measure again after 5 minutes of rest at the same time tomorrow, limit salt and keep regular exercise.", 2),
            ("cardio_z2", "Light aerobic session", "20-30 min zone-2 on the cycle ergometer; skip maximal efforts for 48 h.", 2)],
 "musculoskeletal": [("resist", "Restore resistance training", "Resume the resistance protocol: 3 sets on major lower-body lifts, at least 4 sessions per week.", 3)],
 "immunity": [("infection", "Limit close contact and report temperature", "If your temperature stays raised, limit close contact with crewmates, drink fluids and contact the flight surgeon.", 3),
              ("sleep_light", "Sleep and light adjustment", "Fix a 8.5 h sleep window; dim blue-rich light 2 h before bed, bright light after waking.", 3),
              ("nutrition", "Nutrition reminder", "Log meals for 3 days; check protein, vitamin D and hydration.", 1)],
 "radiation": [("shelter", "Move to the shielded shelter", "Stay in the best-shielded area of the habitat until the ground team confirms the event has passed.", 4)],
 "mental": [("social", "Shared meal or call", "Schedule a 30-min shared meal or conversation with a crewmate today.", 3),
            ("private_call", "Private support call", "Request a scheduled private call with family or the psychological support team.", 2),
            ("workload", "Workload relief", "Defer one non-critical task this week.", 1)],
}

def recommend(scores, overall, fb):
    recs = []
    for sy in SYSTEMS:
        sc = scores[sy]
        if sc < 75:
            for rid, title, action, p in CATALOG[sy]:
                up, down = fb.get(rid, (0, 0))
                pri = p * (2 if sc < 50 else 1) + (up - down) / (up + down + 1)
                recs.append(dict(id=rid, system=sy, title=title, action=action, priority=round(pri, 2),
                                 severity="red" if sc < 50 else "amber"))
    recs.sort(key=lambda r: -r["priority"])
    reds = [s for s in SYSTEMS if scores[s] < 50]
    escalate = scores["mental"] < 40 or scores.get("radiation", 100) < 50 or len(reds) >= 2 or overall < 40
    return recs, escalate
