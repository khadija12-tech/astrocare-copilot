"""Mission routine prompts + gentle gamification. No penalties: the goal is useful data, not perfection."""
TASKS = [
 dict(id="checkin", title="30-second check-in", minutes="1 min", cadence="daily", system="mental", why="Mood and fatigue catch strain that sensors miss."),
 dict(id="pulse", title="Resting pulse", minutes="2 min", cadence="daily", system="cardio", why="A calm morning pulse is your most reliable heart signal."),
 dict(id="dosimeter", title="Read the radiation dosimeter", minutes="1 min", cadence="daily", system="radiation", why="Radiation cannot be felt. The dosimeter is how you know."),
 dict(id="exercise", title="Exercise session", minutes="45 min", cadence="daily", system="musculoskeletal", why="Training replaces the load that gravity normally gives your bones and muscles."),
 dict(id="sleep", title="Review last night's sleep", minutes="1 min", cadence="daily", system="immunity", why="Sleep is the base for mood and immunity."),
 dict(id="meal", title="Share a meal or call with a crewmate", minutes="30 min", cadence="daily", system="mental", why="Regular contact protects against isolation."),
 dict(id="selfcheck", title="Self-check: blood pressure, glucose, temperature", minutes="5 min", cadence="daily", system="metabolic", why="These three readings catch problems that heart rate and sleep miss."),
 dict(id="voice", title="10-second voice sample", minutes="1 min", cadence="weekly", system="mental", why="Voice changes can show tiredness early."),
]
CORE = ["checkin", "pulse", "dosimeter"]
SYSTEM_OF = {t["id"]: t["system"] for t in TASKS}
LEVELS = ["Cadet", "Navigator", "Flight engineer", "Commander"]

def tasks_for(day, scores):
    out = []
    for t in TASKS:
        urgent = scores.get(t["system"], 100) < 75
        due = t["cadence"] == "daily" or day % 7 == 0 or urgent
        out.append({**t, "due": due, "urgent": urgent})
    return sorted(out, key=lambda x: (not x["urgent"], not x["due"]))

def _score(g, d, system):
    row = g[g.day == d]
    return float(row.iloc[0]["score_" + system]) if len(row) else 100.0

def gamify(done, g, day):
    per_day, pts = {}, 0
    for d, tid in done:
        per_day.setdefault(d, set()).add(tid)
        pts += 20 if _score(g, d, SYSTEM_OF[tid]) < 75 else 10   # double points when the task mattered most
    complete = lambda d: all(c in per_day.get(d, set()) for c in CORE)
    d, streak = (day if complete(day) else day - 1), 0
    while d >= 0 and complete(d): streak += 1; d -= 1
    badges = []
    if done: badges.append(("First step", "Completed a first task."))
    if streak >= 3: badges.append(("Steady routine", "All core tasks 3 days in a row."))
    if streak >= 7: badges.append(("Week strong", "All core tasks 7 days in a row."))
    if any(t == "checkin" and _score(g, d, "mental") < 75 for d, t in done): badges.append(("Early reporter", "Checked in while mental score was below normal."))
    if any(t == "dosimeter" and _score(g, d, "radiation") < 75 for d, t in done): badges.append(("Shield ready", "Read the dosimeter during a radiation alert."))
    if sum(1 for _, t in done if t == "meal") >= 5: badges.append(("Crew first", "Shared 5 meals or calls with the crew."))
    return dict(points=pts, level=LEVELS[min(pts // 100, 3)], streak=streak, badges=badges)
