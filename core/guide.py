"""Plain-language guide: what each indicator is, how to measure it, why it matters. Not medical advice."""
GUIDE = {
 "rhr": dict(what="Heartbeats per minute when you are calm.", how="On waking, before moving: wear the band overnight, or sit still for 5 minutes and count your pulse for 60 seconds.", why="It creeps up with fatigue, stress, poor sleep or illness."),
 "hrv": dict(what="How much the time between heartbeats varies. Higher usually means better recovery.", how="Measured by the wearable during sleep. No action needed.", why="It drops when the body is under strain, often before you feel it."),
 "exercise_min": dict(what="Minutes of resistance and aerobic training.", how="Log each session on the exercise device or in the app.", why="Gravity normally loads bones and muscles. In space that load is reduced, so training replaces it."),
 "sleep_h": dict(what="Hours actually asleep.", how="Measured by the wearable. Review it each morning.", why="Short sleep weakens mood, attention and immune resilience."),
 "sleep_eff": dict(what="Share of the time in bed that you were asleep.", how="Measured by the wearable.", why="Low efficiency means broken sleep, often from light, noise or stress."),
 "immune_idx": dict(what="A demo index of how stressed the immune system is (higher is worse). In real use it would come from blood or saliva markers.", how="From periodic samples. The demo value is simulated.", why="Closed habitats and stress can change immune responses."),
 "mood": dict(what="How you feel, from 0 (very low) to 10 (very good).", how="Move the slider in the 30-second check-in.", why="Mood changes are an early sign of strain in long isolation."),
 "fatigue": dict(what="How tired you feel, from 0 (fresh) to 10 (exhausted).", how="Move the slider in the 30-second check-in.", why="Fatigue raises the risk of mistakes during critical tasks."),
 "voice_pitch_var": dict(what="How much your voice pitch moves while you speak.", how="Read any sentence aloud for 10 seconds in the Voice tab.", why="A flatter voice can go with fatigue or low mood."),
 "speech_rate": dict(what="How fast you speak, in syllables per second.", how="Same 10-second voice sample.", why="Slower speech can go with tiredness."),
 "social_min": dict(what="Minutes spent talking or eating with crewmates.", how="Logged from shared meals and calls.", why="Withdrawing from the crew is an early warning sign in isolation."),
 "bp_sys": dict(what="The pressure in your arteries when the heart beats (top number).", how="Automatic arm cuff after 5 minutes of rest, arm at heart level.", why="High pressure often has no symptoms, and long missions can strain the heart and vessels."),
 "glucose": dict(what="Sugar in your blood, in mg/dL. Both very low and very high values matter.", how="Fingerstick meter or a worn sensor, noting whether you fasted for 8 hours.", why="Diet, activity and stress change in space, and low sugar can cause confusion quickly."),
 "temp": dict(what="Body temperature in degrees Celsius.", how="Forehead or ear thermometer after 15 minutes of rest.", why="A rise can be the first sign of infection, which spreads fast in a closed habitat."),
 "radiation_dose": dict(what="Radiation dose rate from your personal dosimeter.", how="Read the dosimeter once a day and whenever an alert sounds.", why="A sudden rise can mean a solar particle event: go to the shielded area."),
}

COLORS = [("green", "75 to 100", "Normal for you. Keep your routine."),
          ("amber", "50 to 74", "Drifting from your baseline. Read the reason and follow the first suggestion."),
          ("red", "below 50", "Act now. Follow the suggested action and contact the ground team if advised.")]

HAZARD_PLAIN = {
 "radiation": "Space radiation cannot be seen or felt. A dosimeter and shelter procedures keep exposure low.",
 "isolation": "Living in a small group, far from home, for a long time changes mood and teamwork. Check in often and keep contact with the crew.",
 "distance": "Help and supplies take longer to arrive the farther you go, so the crew must handle problems on board first.",
 "gravity": "Muscles, bones, inner ear and organs must adjust to different gravity, so regular exercise matters.",
 "closed": "A spacecraft is also a machine. Temperature, air, light, noise and microbes all affect how you feel and sleep.",
}

# NASA HRP "Risks of Human Spaceflight" (nasa.gov/hrp/risks) vs. what AstroCare does. Honest coverage.
RISKS = [
 ("Altered immune system responses", "Immunity and sleep score: immune stress index, temperature, sleep", "Covered"),
 ("Cardiovascular adaptations", "Cardiovascular score: blood pressure, heart rate, HRV; Self-check", "Covered"),
 ("Reduced cardiorespiratory and musculoskeletal fitness", "Exercise-load signal, bone and muscle score, exercise recommendations", "Covered"),
 ("Behavioral changes and psychiatric disorders", "Mood, fatigue, voice, social time, 30-second check-in, escalation to the ground", "Covered"),
 ("Inadequate teamwork", "Crew dynamics: pair sentiment, contact time, isolation table", "Covered"),
 ("Inadequate sleep and irregular schedules", "Sleep signals, light and sleep recommendations, daily routine", "Covered"),
 ("Spaceflight-induced bone changes", "Bone and muscle score uses exercise as a proxy; no bone measurement", "Partly"),
 ("Inadequate food and nutrition", "Metabolic score (glucose), meal log task, nutrition reminders", "Partly"),
 ("Host-microorganism interactions", "Temperature and infection alert with advice to limit close contact", "Partly"),
 ("Spaceflight Associated Neuro-ocular Syndrome (SANS)", "Vision-change prompt in Self-check that advises reporting it", "Partly"),
 ("Altered sensorimotor and vestibular function", "Dizziness or coordination prompt in Self-check", "Partly"),
 ("Radiation-induced cancers", "Radiation dose-rate signal, cumulative dose, shelter advice (monitoring only)", "Partly"),
 ("Decompression sickness", "Not in scope", "Not in scope"),
 ("Hypoxia", "Not in scope", "Not in scope"),
 ("Injury and compromised performance from spacewalks", "Not in scope", "Not in scope"),
 ("Inadequate systems operations support", "Not in scope", "Not in scope"),
 ("Injury from dynamic loads", "Not in scope", "Not in scope"),
]
