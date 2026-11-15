# AstroCare Copilot - AI-assisted code (generated with Claude, reviewed by the team)
SIGNALS = {
    "rhr":             dict(label="Resting heart rate",       unit="bpm",    bad=+1, system="cardio"),
    "hrv":             dict(label="Heart-rate variability",   unit="ms",     bad=-1, system="cardio"),
    "exercise_min":    dict(label="Exercise load",            unit="min",    bad=-1, system="musculoskeletal"),
    "sleep_h":         dict(label="Sleep duration",           unit="h",      bad=-1, system="immunity"),
    "sleep_eff":       dict(label="Sleep efficiency",         unit="",       bad=-1, system="immunity"),
    "immune_idx":      dict(label="Immune stress index",      unit="",       bad=+1, system="immunity"),
    "mood":            dict(label="Mood (self-report)",       unit="/10",    bad=-1, system="mental"),
    "fatigue":         dict(label="Fatigue (self-report)",    unit="/10",    bad=+1, system="mental"),
    "voice_pitch_var": dict(label="Voice pitch variability",  unit="st",     bad=-1, system="mental"),
    "speech_rate":     dict(label="Speech rate",              unit="syl/s",  bad=-1, system="mental"),
    "social_min":      dict(label="Social time",              unit="min",    bad=-1, system="mental"),
    "radiation_dose":  dict(label="Radiation dose rate (simulated)", unit="mSv/day", bad=+1, system="radiation"),
    "bp_sys":          dict(label="Systolic blood pressure", unit="mmHg",    bad=+1, system="cardio"),
    "glucose":         dict(label="Blood glucose",           unit="mg/dL",   bad=0,  system="metabolic"),
    "temp":            dict(label="Body temperature",        unit="°C",      bad=0,  system="immunity"),
}
# bad=+1: higher is worse, -1: lower is worse, 0: any large change is a warning (two-sided)
SYSTEMS = ["cardio", "musculoskeletal", "immunity", "metabolic", "mental", "radiation"]
SYSTEM_LABEL = {"cardio": "Cardiovascular", "musculoskeletal": "Bone & muscle",
                "immunity": "Immunity & sleep", "mental": "Mental & social", "radiation": "Radiation", "metabolic": "Metabolic & nutrition"}
BASELINE_DAYS = 21
ICON = {"green": "🟢", "amber": "🟡", "red": "🔴"}

def status(score):
    return "green" if score >= 75 else "amber" if score >= 50 else "red"

# NASA Human Research Program: the five hazards of human spaceflight (nasa.gov/hrp/hazards)
HAZARDS = {
    "radiation": ("Space radiation", "https://www.nasa.gov/hrp/hazard-space-radiation/"),
    "isolation": ("Isolation and confinement", "https://www.nasa.gov/hrp/hazard-isolation-and-confinement/"),
    "distance":  ("Distance from Earth", "https://www.nasa.gov/hrp/hazard-distance-from-earth/"),
    "gravity":   ("Gravity fields", "https://www.nasa.gov/hrp/hazard-gravity-fields/"),
    "closed":    ("Hostile/closed environments", "https://www.nasa.gov/hrp/hazard-hostile-closed-environments/"),
}
SYSTEM_HAZARD = {"cardio": "gravity", "musculoskeletal": "gravity", "immunity": "closed",
                 "mental": "isolation", "radiation": "radiation", "metabolic": "distance"}

ENVIRONMENTS = {
    "Spacecraft in deep-space transit": dict(delay=20, delay_text="up to roughly 20 minutes one-way (Mars distance)", gravity="microgravity", tips={
        "musculoskeletal": "Microgravity unloads bones and muscles: keep the daily resistance routine.",
        "cardio": "Keep aerobic sessions light and regular; avoid sudden maximal efforts.",
        "immunity": "A closed cabin: keep light, noise and the sleep schedule steady.",
        "mental": "Small crew, long isolation: protect shared meals and private calls.",
        "metabolic": "Food choices are limited far from Earth: keep regular meals and log them.",
        "radiation": "Deep space: follow the storm-shelter procedure and tell the ground team."}),
    "Space station (low Earth orbit)": dict(delay=0, delay_text="near real time", gravity="microgravity", tips={
        "musculoskeletal": "Microgravity unloads bones and muscles: use the resistance device daily.",
        "cardio": "Keep aerobic sessions regular; follow the flight surgeon's plan.",
        "immunity": "Keep the sleep window and cabin light steady.",
        "mental": "Use the regular calls home and crew meals.",
        "metabolic": "Keep regular meals and log them for the ground nutrition team.",
        "radiation": "Follow the station's shelter procedure and tell the ground team."}),
    "Lunar base": dict(delay=0, delay_text="about 1 to 2 seconds one-way (near real time)", gravity="about one-sixth of Earth's", tips={
        "musculoskeletal": "Partial gravity loads bones less than Earth: keep loaded exercise and walking.",
        "cardio": "Build aerobic work back up gradually after long suited activity.",
        "immunity": "Keep a regular sleep window; the day-night cycle is not Earth's.",
        "mental": "Plan regular crew time; work shifts can keep people apart.",
        "metabolic": "Keep regular meals; plan food supplies with the ground team.",
        "radiation": "Go to the base's best-shielded area and follow the shelter procedure."}),
    "Mars base or rover": dict(delay=20, delay_text="roughly 3 to 22 minutes one-way", gravity="about three-eighths of Earth's", tips={
        "musculoskeletal": "Partial gravity still loads bones less than Earth: keep loaded exercise.",
        "cardio": "Keep aerobic training regular and track recovery.",
        "immunity": "Keep a steady sleep window and light schedule.",
        "mental": "Long delay and distance: rely on the crew, and queue messages to the ground.",
        "metabolic": "Long delay means slow resupply: log meals and ration carefully.",
        "radiation": "Go to the best-shielded area and follow the shelter procedure."}),
}
