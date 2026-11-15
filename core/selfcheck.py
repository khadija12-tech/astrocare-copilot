"""Self-check: absolute reference ranges for common indicators, with plain guidance.
General adult ranges. The mission medical protocol and the flight surgeon always take priority.
Decision support only, not a diagnosis. AI-assisted code: ranges must be reviewed by a clinician."""
import numpy as np

INFO = {
 "bp": dict(label="Blood pressure", unit="mmHg", hazard="gravity",
            measure="Automatic arm cuff. Sit quietly for 5 minutes, arm at heart level, take two readings a minute apart and record the second.",
            why="High blood pressure usually causes no symptoms, so only measuring reveals it.",
            space="Microgravity shifts body fluids toward the head and reduces the load on the heart and vessels. Long missions can also reduce fitness."),
 "hr": dict(label="Resting heart rate", unit="bpm", hazard="gravity",
            measure="Wearable overnight, or count your pulse for 60 seconds after 5 minutes of rest.",
            why="A heart rate unusually high or low for you is one of the earliest signs of strain, dehydration or illness.",
            space="Less gravity and less exercise change how hard the heart works. Stress and poor sleep raise resting heart rate."),
 "glucose": dict(label="Blood glucose", unit="mg/dL", hazard="distance",
            measure="Fingerstick meter or a worn glucose sensor from the mission medical kit. Note whether you fasted for 8 hours.",
            why="Very low blood sugar can cause confusion quickly. Persistently high values can signal a metabolic problem.",
            space="Food choices are limited and resupply is far, and activity, schedules and stress can all change glucose."),
 "temp": dict(label="Body temperature", unit="°C", hazard="closed",
            measure="Forehead or ear thermometer, away from vents, after 15 minutes of rest.",
            why="Fever points to infection or inflammation, and a sealed crew can pass infections to each other quickly.",
            space="Closed habitats and changed immune responses make early detection of infection important."),
 "sleep": dict(label="Sleep last night", unit="h", hazard="closed",
            measure="Wearable sleep log, or write down bedtime and wake time.",
            why="Sleep loss lowers alertness, mood and immune resilience.",
            space="Light, noise, shift work and the lack of a normal day-night cycle all disrupt sleep."),
 "mood": dict(label="Mood", unit="/10", hazard="isolation",
            measure="Move the 0 to 10 slider (0 very low, 10 very good).",
            why="Mood shifts are an early sign of behavioural-health strain.",
            space="Isolation, confinement and distance from family and Earth weigh on mood over time."),
}
BANDS = {"bp": (90, 119), "hr": (50, 100), "glucose": (70, 99), "temp": (36.1, 37.2), "sleep": (7, 10), "mood": (6, 10)}
CALL_ANY_TIME = "Contact the flight surgeon for any result you are unsure about."

def _r(status, meaning, do, prevent=(), call=None, urgent=False):
    return dict(status=status, meaning=meaning, do=list(do), prevent=list(prevent), call=call, urgent=urgent)

def assess_bp(s, d):
    if s >= 180 or d >= 120:
        return _r("red", "Very high: possible hypertensive crisis.", ["Alert a crewmate and the ground now.", "Stay seated and rest. Take no medication unless the flight surgeon instructs it."], call="Now", urgent=True)
    if s >= 140 or d >= 90:
        return _r("red", "High (stage 2 range).", ["Rest 5 minutes and measure again.", "If it is still high, contact the flight surgeon today.", "Take medication only as the flight surgeon instructs."],
                  ["Keep regular aerobic and resistance exercise.", "Limit salt, drink enough, protect sleep."], call="Today if confirmed")
    if s >= 130 or d >= 80:
        return _r("amber", "Raised (stage 1 range).", ["Measure again tomorrow at the same time of day.", "Tell the ground team if it stays raised for 3 days."], ["Keep regular exercise.", "Limit salt, protect sleep."], call="If raised for 3 days")
    if s >= 120:
        return _r("amber", "Slightly elevated.", ["Measure again tomorrow."], ["Keep regular exercise and sleep."])
    if s < 90 or d < 60:
        return _r("amber", "Low.", ["Sit or lie down and drink fluids. Stand up slowly.", "If you feel faint or dizzy, tell a crewmate and the ground team."], call="If you feel faint")
    return _r("green", "Normal range.", ["Keep your routine."])

def assess_hr(v):
    if v >= 120 or v < 40:
        return _r("red", "Very fast at rest." if v >= 120 else "Very slow at rest.", ["Sit and rest 10 minutes, then measure again.", "If it is still outside 40 to 120, contact the flight surgeon now."], call="Now if confirmed")
    if v > 100 or v < 50:
        return _r("amber", "Fast at rest." if v > 100 else "Slow at rest (can be normal for very fit people).", ["Rest, drink fluids, measure again in an hour.", "Compare with your own baseline."], ["Protect sleep, limit caffeine late in the day."], call="If it stays this way for 2 days")
    return _r("green", "Normal range. Compare with your own baseline.", ["Keep your routine."])

def assess_glucose(v, fasting):
    if v < 54:
        return _r("red", "Very low blood sugar.", ["Treat now: about 15 g fast-acting sugar (juice or glucose tablets).", "Recheck in 15 minutes and repeat if still below 70.", "Tell a crewmate and the ground team."], call="Now", urgent=True)
    if v < 70:
        return _r("amber", "Low blood sugar.", ["Take about 15 g fast-acting carbohydrate (juice or glucose tablets).", "Recheck in 15 minutes and repeat if still below 70."], ["Do not skip meals; keep a fast sugar source within reach."], call="If it happens again")
    hi_red, hi_amber = (126, 100) if fasting else (200, 140)
    if v >= hi_red:
        return _r("red", "High." + (" Fasting value in the diabetes range." if fasting else ""), ["Repeat the measurement.", "If it is still high, contact the flight surgeon today."], ["Review meals and activity with the ground nutrition team."], call="Today if confirmed")
    if v >= hi_amber:
        return _r("amber", "Above the usual range.", ["Repeat tomorrow under the same conditions (fasting or not)."], ["Keep daily exercise, review meals with the ground nutrition team."], call="If it stays high for 3 days")
    return _r("green", "Normal range.", ["Keep your routine."])

def assess_temp(t):
    if t >= 38.0:
        return _r("red", "Fever.", ["Rest and drink fluids. Measure again in an hour.", "Limit close contact with crewmates.", "Contact the flight surgeon: infections spread quickly in a closed habitat."], call="Today")
    if t < 35.0:
        return _r("red", "Low body temperature.", ["Warm up with extra layers and a warm drink.", "Measure again in 30 minutes and contact the flight surgeon if still low."], call="Now if it stays low")
    if t >= 37.3 or t < 36.1:
        return _r("amber", "Slightly raised." if t >= 37.3 else "Slightly low.", ["Measure again in a few hours.", "Watch for other symptoms such as cough or aches."], call="If it reaches 38.0 °C")
    return _r("green", "Normal range.", ["Keep your routine."])

def assess_sleep(h):
    if h < 5:
        return _r("red", "Very short sleep.", ["Protect a full sleep window tonight and reduce non-critical tasks.", "Tell the crew lead and the ground team if it repeats."], ["Dim blue-rich light 2 hours before bed."], call="If it repeats")
    if h < 7:
        return _r("amber", "Short sleep.", ["Aim for a longer sleep window tonight."], ["Dim blue-rich light 2 hours before bed, bright light after waking."], call="If it repeats for 3 nights")
    return _r("green", "Enough sleep.", ["Keep your routine."])

def assess_mood(m):
    if m < 4:
        return _r("red", "Low mood.", ["Talk to a crewmate or request a private call with the psychological support team.", "Plan one thing you enjoy today."], ["Keep shared meals and exercise."], call="Request a private call")
    if m < 6:
        return _r("amber", "Mood below your usual range.", ["Spend 30 minutes with a crewmate or call home."], ["Keep shared meals, exercise and sleep regular."], call="If it lasts 3 days")
    return _r("green", "Good.", ["Keep your routine."])

def assess(reads):
    return {"bp": assess_bp(*reads["bp"]), "hr": assess_hr(reads["hr"]), "glucose": assess_glucose(*reads["glucose"]),
            "temp": assess_temp(reads["temp"]), "sleep": assess_sleep(reads["sleep"]), "mood": assess_mood(reads["mood"])}

def to_reads(d):
    return dict(bp=(d["sys"], d["dia"]), hr=d["hr"], glucose=(d["glucose"], bool(d["fasting"])), temp=d["temp"], sleep=d["sleep"], mood=d["mood"])

def demo_readings(day, n=10, seed=5):
    """Simulated sample history with a slowly rising blood pressure and falling sleep/mood."""
    rng = np.random.default_rng(seed); rows = []
    for i in range(n):
        k = i / (n - 1)
        rows.append(dict(day=day - n + 1 + i, sys=round(116 + 22 * k + rng.normal(0, 2)), dia=round(74 + 12 * k + rng.normal(0, 2)),
                         hr=round(62 + 10 * k + rng.normal(0, 1.5)), glucose=round(90 + 12 * k + rng.normal(0, 3)), fasting=1,
                         temp=round(36.6 + rng.normal(0, .15), 1), sleep=round(7.2 - 1.4 * k + rng.normal(0, .2), 1), mood=round(7.5 - 2.5 * k + rng.normal(0, .3), 1)))
    return rows
