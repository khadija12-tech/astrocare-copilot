# AstroCare Copilot - AI-assisted code (generated with Claude, reviewed by the team)
import json, pathlib, numpy as np, pandas as pd, plotly.graph_objects as go, streamlit as st
from plotly.subplots import make_subplots
from core.config import SIGNALS, SYSTEMS, SYSTEM_LABEL, BASELINE_DAYS, ICON, status, HAZARDS, SYSTEM_HAZARD, ENVIRONMENTS
from core.guide import GUIDE, COLORS, HAZARD_PLAIN, RISKS
from core import selfcheck as sc, routine as rt, simulator, analysis as an, recommend as rc, projection as pj, crew as cw, voice as vc, delay as dl, db

st.set_page_config(page_title="AstroCare Copilot", page_icon="🚀", layout="wide", initial_sidebar_state="collapsed")
db.init()

@st.cache_data
def load_sim():
    df = simulator.simulate(); return df, simulator.simulate_interactions(df)

@st.cache_data
def run_analysis(df):
    return an.analyze(df)

NASA_CSV = pathlib.Path(__file__).resolve().parent / "data" / "nasa" / "OSD-575_LSDS-8_CMP_TRANSFORMED.csv"
UNITS = {"gram_per_deciliter": "g/dL", "milligram_per_deciliter": "mg/dL", "units_per_liter": "U/L", "millimol_per_liter": "mmol/L",
         "milliliter_per_minute_per_1.73_meter_squared": "mL/min/1.73 m²"}
TP_ORDER = ["L-92", "L-44", "L-3", "R+1", "R+45", "R+82", "R+194"]

@st.cache_data
def load_cmp():
    """NASA OSDR OSD-575 (Inspiration4) comprehensive metabolic panel, long format."""
    raw = pd.read_csv(NASA_CSV); parts = raw["Sample Name"].str.split("_", expand=True)
    raw["crew"], raw["tp"] = parts[0], parts[2]; rows = []
    for c in raw.columns:
        if "_value" not in c: continue
        base, _, unit = c.partition("_value"); unit = unit.lstrip("_")
        rmin = next((x for x in raw.columns if x.startswith(base + "_range_min")), None)
        rmax = next((x for x in raw.columns if x.startswith(base + "_range_max") or x.startswith(base + "_max")), None)
        label = " ".join(w.upper() if w in ("alt", "ast", "bun", "egfr") else w.capitalize() for w in base.split("_"))
        for _, r in raw.iterrows():
            rows.append(dict(crew=r.crew, tp=r.tp, order=TP_ORDER.index(r.tp), analyte=base, label=label, unit=UNITS.get(unit, unit.replace("_", " ")),
                             value=r[c], rmin=r[rmin] if rmin else np.nan, rmax=r[rmax] if rmax else np.nan))
    return pd.DataFrame(rows)

def apply_checkins(df):
    df = df.copy()
    for name, day, mood, fat, _ in db.checkins():
        m = (df.astronaut == name) & (df.day == day)
        df.loc[m, "mood"] = mood; df.loc[m, "fatigue"] = fat
    return df

# ---------- sidebar ----------
with st.sidebar:
    st.header("Controls")
    src = st.radio("Data source", ["Simulated crew", "Upload CSV"])
    up = st.file_uploader("CSV: day, astronaut + signal columns", type="csv") if src == "Upload CSV" else None
    env_name = st.selectbox("Environment", list(ENVIRONMENTS))
    env = ENVIRONMENTS[env_name]
    delay_min = st.slider("One-way comms delay (min)", 0, 24, env["delay"], key="delay_" + env_name)

df, inter = load_sim()
if up is not None:
    d2 = pd.read_csv(up); missing = [c for c in ["day", "astronaut", *SIGNALS] if c not in d2.columns]
    if missing: st.sidebar.error("Missing columns: " + ", ".join(missing))
    else: df = d2; inter = simulator.simulate_interactions(df)
df = apply_checkins(df)
A, stats, det = run_analysis(df)

names = sorted(A.astronaut.unique())
c1, c2 = st.columns([1, 2])
name = c1.selectbox("Astronaut", names, index=names.index("Amira") if "Amira" in names else 0)
dmax = int(A.day.max())
day = c2.slider("Mission day (replay)", BASELINE_DAYS, dmax, dmax)
g = A[A.astronaut == name].reset_index(drop=True); gd = g[g.day <= day]
row = g[g.day == day].iloc[0]; mu, sd = stats[name]
scores = {s: float(row["score_" + s]) for s in SYSTEMS}; ov = float(row.overall)
items = an.explain(g, stats[name], day)
recs, escalate = rc.recommend(scores, ov, db.feedback_stats())

st.title("🚀 AstroCare Copilot")
st.caption("Offline health copilot that learns each astronaut's personal baseline, flags drift early, explains why, and suggests actions. "
           "**Decision support, not a medical diagnosis.** Demo data is SIMULATED.")
st.caption(f"**{env_name}**: gravity {env['gravity']}; radio delay {env['delay_text']}.")

TAB_NAMES = ["Today", "Self-check", "Routine", "Why", "Action", "Crew", "Voice", "30-day twin", "Earth link", "Learn", "Real NASA data", "NASA evidence"]
T = dict(zip(TAB_NAMES, st.tabs(TAB_NAMES)))
BADGE = {"green": "green", "amber": "orange", "red": "red"}

def sig_fig(sg):
    fig = go.Figure(go.Scatter(x=gd.day, y=gd[sg], mode="lines"))
    fig.add_hrect(y0=mu[sg] - 2 * sd[sg], y1=mu[sg] + 2 * sd[sg], fillcolor="green", opacity=.12, line_width=0)
    fig.add_vline(x=BASELINE_DAYS, line_dash="dot", annotation_text="baseline ends")
    fig.update_layout(title=f"{SIGNALS[sg]['label']} ({SIGNALS[sg]['unit']})", height=250, margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
    return fig

def hz_link(h):
    return f"[{HAZARDS[h][0]}]({HAZARDS[h][1]})"

# ---------- Today ----------
with T["Today"]:
    cols = st.columns(len(SYSTEMS))
    for col, sy in zip(cols, SYSTEMS):
        stt = status(scores[sy]); col.metric(SYSTEM_LABEL[sy], f"{ICON[stt]} {scores[sy]:.0f}/100")
        col.markdown({"green": ":green-badge[Normal]", "amber": ":orange-badge[Watch]", "red": ":red-badge[Act now]"}[stt])
    st.caption(f"Cumulative simulated radiation dose so far: {gd.radiation_dose.sum():.0f} mSv. The ground team tracks career dose limits.")
    with st.expander("How to read the colours"):
        for c, r, m in COLORS: st.markdown(f":{BADGE[c]}-badge[{c.title()}, {r}] {m}")
    st.subheader(an.headline(scores, items))
    if items:
        st.write("**Top driver:** " + items[0]["text"])
        hz = sorted({SYSTEM_HAZARD[SIGNALS[i["signal"]]["system"]] for i in items})
        st.caption("NASA hazards involved: " + ", ".join(hz_link(h) for h in hz))
    dd = det.get(name)
    if dd is not None and day >= dd:
        st.warning(f"Drift first detected on mission day {dd + 1}, while most single readings were still inside normal ranges.")
    with st.expander("30-second check-in (self-report)"):
        a, b, c = st.columns(3)
        mood = a.slider("Mood", 0, 10, int(round(row.mood))); fat = b.slider("Fatigue", 0, 10, int(round(row.fatigue)))
        ten = c.slider("Tension", 0, 10, 3)
        if st.button("Save check-in"):
            db.add_checkin(name, day, mood, fat, ten); st.rerun()

# ---------- Why ----------
with T["Why"]:
    for t in an.interpret(items): st.info(t)
    if not items: st.success("No signal outside the astronaut's personal normal band.")
    shown = [i["signal"] for i in items[:4]] or ["rhr", "sleep_h"]
    cols = st.columns(2)
    for k, sg in enumerate(shown):
        cols[k % 2].plotly_chart(sig_fig(sg), width="stretch", key="why_" + sg)
        with cols[k % 2].expander("What is this?"):
            gd_ = GUIDE[sg]; st.write(f"**What:** {gd_['what']}"); st.write(f"**How to measure:** {gd_['how']}"); st.write(f"**Why it matters:** {gd_['why']}")
    fig = go.Figure(go.Scatter(x=gd.day, y=gd.iso_score, mode="lines", name="anomaly score"))
    fig.update_layout(title="Isolation Forest anomaly score (multi-signal, higher = more unusual)", height=230, margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig, width="stretch")
    st.caption("Green band = personal normal (baseline mean ± 2 SD from the first 21 days).")
    pick_s = st.selectbox("Explore any indicator", list(SIGNALS), format_func=lambda x: SIGNALS[x]["label"])
    st.plotly_chart(sig_fig(pick_s), width="stretch", key="why_explore")

# ---------- Action ----------
with T["Action"]:
    if escalate: st.error("Discuss with the flight surgeon on the ground: several systems or mental health are in the red.")
    if not recs: st.success("No action needed today. Keep the routine.")
    for r in recs[:5]:
        with st.container(border=True):
            st.markdown(f"**{ICON[r['severity']]} {r['title']}** ({SYSTEM_LABEL[r['system']]})")
            st.write(r["action"])
            st.caption("NASA hazard: " + hz_link(SYSTEM_HAZARD[r["system"]]))
            if env["tips"].get(r["system"]): st.caption("In this environment: " + env["tips"][r["system"]])
            u, d_, _ = st.columns([1, 1, 6])
            if u.button("Helped", key="up" + r["id"]): db.add_feedback(r["id"], True); st.rerun()
            if d_.button("No help", key="dn" + r["id"]): db.add_feedback(r["id"], False); st.rerun()
    st.caption("Feedback re-ranks future recommendations on this device. Limits: rules are illustrative and must be validated by flight surgeons.")

# ---------- Crew ----------
with T["Crew"]:
    ps = cw.pair_summary(inter, day); iso = cw.isolation_table(A[A.day <= day], stats, day)
    pos = {n: (np.cos(2 * np.pi * i / len(names)), np.sin(2 * np.pi * i / len(names))) for i, n in enumerate(names)}
    fig = go.Figure(); col = {"ok": "#22c55e", "watch": "#f59e0b", "tension": "#ef4444"}
    for _, p in ps.iterrows():
        if p.a in pos and p.b in pos:
            fig.add_trace(go.Scatter(x=[pos[p.a][0], pos[p.b][0]], y=[pos[p.a][1], pos[p.b][1]], mode="lines",
                                     line=dict(width=max(1, p.minutes / 6), color=col[p.status]), hoverinfo="skip", showlegend=False))
    ov_now = {n: float(A[(A.astronaut == n) & (A.day == day)].overall.iloc[0]) for n in names}
    fig.add_trace(go.Scatter(x=[pos[n][0] for n in names], y=[pos[n][1] for n in names], mode="markers+text", text=names, textposition="top center",
                             marker=dict(size=34, color=[{"green": "#22c55e", "amber": "#f59e0b", "red": "#ef4444"}[status(ov_now[n])] for n in names]), showlegend=False))
    fig.update_layout(height=380, xaxis=dict(visible=False, range=[-1.5, 1.5]), yaxis=dict(visible=False, range=[-1.5, 1.5]), margin=dict(l=10, r=10, t=10, b=10))
    l, r_ = st.columns([3, 2]); l.plotly_chart(fig, width="stretch")
    r_.write("**Isolation per astronaut**"); r_.dataframe(iso, hide_index=True)
    st.write("**Pair relationships** (line width = contact time, colour = sentiment change vs baseline)")
    st.dataframe(ps, hide_index=True)
    bad = ps[ps.status == "tension"]
    for _, p in bad.iterrows(): st.warning(f"Tension between {p.a} and {p.b}: sentiment {p.delta:+.2f} vs baseline. Suggest a facilitated conversation with the ground psychologist.")

# ---------- Voice ----------
with T["Voice"]:
    st.write("Voice carries stress signals (flatter pitch, slower speech, longer pauses). Analysis runs **locally**; raw audio is discarded, only 3 numbers are kept.")
    b1, b2 = st.columns(2)
    if b1.button("Try demo: normal voice"): st.session_state["vx"] = vc.synth_voice("normal")
    if b2.button("Try demo: fatigued voice"): st.session_state["vx"] = vc.synth_voice("tired")
    rec = st.audio_input("Or record 5-10 s of normal speech") if hasattr(st, "audio_input") else None
    if rec is not None:
        try: st.session_state["vx"] = vc.read_wav(rec.getvalue())
        except Exception as e: st.error(f"Could not read the recording: {e}")
    if "vx" in st.session_state:
        try:
            f = vc.analyze(st.session_state["vx"])
            m = st.columns(3)
            m[0].metric("Pitch variability (st)", f"{f['pitch_var']:.2f}", f"{f['pitch_var'] - mu['voice_pitch_var']:+.2f} vs baseline")
            m[1].metric("Speech rate (syl/s)", f"{f['speech_rate']:.2f}", f"{f['speech_rate'] - mu['speech_rate']:+.2f} vs baseline")
            m[2].metric("Pause ratio", f"{f['pause_ratio']:.0%}")
            z = (f["pitch_var"] - mu["voice_pitch_var"]) / sd["voice_pitch_var"]
            (st.warning if z < -3 else st.success)("Voice is flatter than this astronaut's baseline." if z < -3 else "Voice within personal baseline.")
            fig = go.Figure(go.Scatter(x=f["t"], y=f["f0"], mode="lines")); fig.update_layout(title="Pitch contour (Hz)", height=240, margin=dict(l=10, r=10, t=40, b=10))
            st.plotly_chart(fig, width="stretch")
            st.audio(vc.to_wav_bytes(st.session_state["vx"]), format="audio/wav")
        except Exception as e: st.error(str(e))

# ---------- Twin ----------
with T["30-day twin"]:
    pr = pj.project(gd, mu, sd); pick = st.selectbox("Curve", ["overall", *SYSTEMS], format_func=lambda x: "Overall" if x == "overall" else SYSTEM_LABEL[x])
    fig = go.Figure()
    for scen, color in (("No change", "#ef4444"), ("Follow plan", "#22c55e")):
        s = pr[pr.scenario == scen]; fig.add_trace(go.Scatter(x=s.day, y=s[pick], name=scen, line=dict(color=color)))
    fig.add_trace(go.Scatter(x=gd.day, y=gd.overall if pick == "overall" else gd["score_" + pick], name="History", line=dict(color="#94a3b8")))
    fig.update_layout(height=380, yaxis=dict(range=[0, 105], title="score"), xaxis_title="mission day", margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, width="stretch")
    a, b = pr[pr.scenario == "No change"].iloc[-1], pr[pr.scenario == "Follow plan"].iloc[-1]
    st.write(f"In 30 days: **{a[pick]:.0f}** if nothing changes vs **{b[pick]:.0f}** if the plan is followed.")
    st.caption("Illustrative digital twin: damped trend vs exponential recovery (5%/day assumed). Not a clinical forecast.")

# ---------- Earth ----------
with T["Earth link"]:
    pkt = dl.build_packet(name, day, scores, ov, items, recs, escalate)
    sc_today = [d for d in db.selfchecks(name) if d["day"] == day]
    if sc_today:
        res_ = sc.assess(sc.to_reads(sc_today[0])); pkt["selfcheck"] = {k: v["status"] for k, v in res_.items()}
        if any(v["urgent"] for v in res_.values()): pkt["priority"] = "URGENT"; pkt["ask_ground"] = True
    full = len(gd.drop(columns=[c for c in gd.columns if c.startswith(("z_", "score_"))]).to_csv(index=False).encode())
    s1, s2, s3 = st.columns(3)
    s1.metric("Priority", pkt["priority"]); s2.metric("Full history", f"{full / 1024:.1f} KB"); s3.metric("Packet to Earth", f"{dl.packet_bytes(pkt)} B")
    st.caption("NASA hazard addressed: " + hz_link("distance") + ". The packet is built and queued on board, so the crew stays autonomous.")
    st.json(pkt)
    st.write(f"**Timeline at {delay_min} min one-way delay**")
    st.table(pd.DataFrame(dl.timeline(delay_min), columns=["When", "What"]))
    st.download_button("Download packet (JSON)", json.dumps(pkt), file_name=f"packet_{name}_day{day + 1}.json")

# ---------- NASA evidence ----------
with T["NASA evidence"]:
    st.write("AstroCare is organised around the five hazards of human spaceflight defined by NASA's Human Research Program. Every alert and recommendation is tagged with its hazard.")
    rows = [("Isolation and confinement", "Crew dynamics, isolation table, voice analysis, 30-second check-in"),
            ("Distance from Earth", "Offline autonomy, delay-mode packet for Earth, prioritised alerts"),
            ("Gravity fields", "Bone and muscle plus cardiovascular scores, exercise recommendations"),
            ("Hostile/closed environments", "Immunity and sleep score, sleep and light recommendations"),
            ("Space radiation", "Radiation dose-rate signal, shelter recommendation, escalation to the ground team")]
    st.table(pd.DataFrame(rows, columns=["NASA hazard", "What AstroCare does"]))
    st.write("NASA says the hazards can feed off one another. AstroCare shows this by linking stress, sleep and immunity in one view.")
    st.markdown("**NASA resource this design follows:** [5 Hazards of Human Spaceflight](https://www.nasa.gov/hrp/hazards/)  \n"
                "**Further reading from the challenge page:** [Risks of Human Spaceflight](https://www.nasa.gov/hrp/risks/), "
                "[Ongoing HRP Research](https://www.nasa.gov/hrp/ongoing-hrp-research/), "
                "[CSA: Monitoring Radiation for Astronaut Health](https://www.asc-csa.gc.ca/eng/news/articles/2026/2026-02-26-monitoring-radiation-astronaut-health.asp)")
    st.info("Data provenance: all crew time series in this demo are SIMULATED (including the day-49 solar particle event). Thresholds and rules are illustrative.")
    st.subheader("How NASA resources shaped the design")
    trace = [("Organise everything by the five hazards and tag every alert", "HRP: 5 Hazards of Human Spaceflight"),
             ("Show interactions (stress, sleep, immunity) in one view", "HRP hazards overview: the hazards can feed off one another"),
             ("Environment selector (station, transit, lunar base, Mars)", "NASA Analog Missions page: analogs and the ISS as test beds for Moon and Mars missions"),
             ("Isolation module: crew tension, voice, check-in", "HRP isolation and confinement hazard; analogs HERA, CHAPEA and Antarctic stations study isolation and health"),
             ("Gravity module: exercise, bone and cardiovascular scores", "HRP gravity fields hazard; analogs :envihab (bedrest), ARGOS and parabolic flight"),
             ("Radiation signal and shelter advice", "HRP space radiation hazard; NASA Space Radiation Laboratory (NSRL)"),
             ("On-board autonomy and delay-mode packet", "HRP distance from Earth hazard; HERA research on isolation, confinement and remote conditions"),
             ("Sleep, activity and light signals from a wearable", "HRP Human Investigations: ARCHeR (Artemis II wrist actigraphy measuring motion, sleep and light exposure)"),
             ("One consistent set of physiological and psychological indicators", "HRP Human Investigations: Standard Measures and Artemis II Standard Measures"),
             ("Immune stress and temperature indicators", "HRP Human Investigations: Artemis II Immune Biomarkers; Altered Immunity"),
             ("Vision-change prompt in Self-check", "HRP Human Investigations: SANS studies (B-Complex, Brain Fluid Pressure, Thigh Cuff, Spinal Fluid Biomarkers)"),
             ("Nutrition reminders and meal log", "HRP Human Investigations: Food Acceptability, Food Physiology"),
             ("Exercise routine and bone and muscle score", "HRP Human Investigations: Zero T2 (exercise in space), Spinal Health"),
             ("Compact health packet for remote review", "HRP Human Investigations: Tempus Pro (telemedicine device integrating health data for remote, near real-time diagnoses)")]
    st.table(pd.DataFrame(trace, columns=["Design decision", "NASA resource"]))
    st.markdown("[Analog Missions](https://www.nasa.gov/analog-missions/) · [HERA](https://www.nasa.gov/mission/hera/) · [CHAPEA](https://www.nasa.gov/humans-in-space/chapea/) · "
                "[Antarctic stations](https://www.nasa.gov/mission/antarctic-stations/) · [:envihab](https://www.nasa.gov/mission/envihab/) · [NSRL](https://www.nasa.gov/mission/nasa-space-radiation-lab/)")
    st.caption("NASA resources guided which hazards, indicators and environments to model. The numbers in this demo are simulated.")
    st.subheader("NASA human-system risks: what AstroCare covers")
    st.markdown("Source: [Risks of Human Spaceflight](https://www.nasa.gov/hrp/risks/) (NASA Human Research Program). We list gaps openly.")
    rk = pd.DataFrame(RISKS, columns=["NASA risk", "How AstroCare addresses it", "Coverage"])
    st.dataframe(rk, hide_index=True)
    st.caption(f"{(rk.Coverage == 'Covered').sum()} covered, {(rk.Coverage == 'Partly').sum()} partly, {(rk.Coverage == 'Not in scope').sum()} not in scope (decompression sickness, hypoxia, spacewalks, systems operations, dynamic loads).")

# ---------- Routine ----------
with T["Routine"]:
    st.write(f"Mission day {day + 1}: today's routine. Each task helps the copilot learn your baseline and spot drift early. Tasks linked to an area that is drifting are marked **needed now**.")
    done_today = {t for d, t in db.tasks(name) if d == day}
    for t in rt.tasks_for(day, scores):
        if not t["due"]: continue
        with st.container(border=True):
            c1, c2 = st.columns([5, 1])
            c1.markdown(f"**{t['title']}** ({t['minutes']})" + (" :red-badge[needed now]" if t["urgent"] else ""))
            c1.caption(t["why"] + (" Use the Voice tab." if t["id"] == "voice" else ""))
            if t["id"] in done_today: c2.markdown(":green-badge[Done]")
            elif c2.button("Done", key="task_" + t["id"]): db.add_task(name, day, t["id"]); st.rerun()
    gm = rt.gamify(db.tasks(name), g, day)
    a, b, c = st.columns(3); a.metric("Points", gm["points"]); b.metric("Level", gm["level"]); c.metric("Streak (days)", gm["streak"])
    st.write("**Badges**")
    if gm["badges"]:
        for bn, bd in gm["badges"]: st.markdown(f":blue-badge[{bn}] {bd}")
    else: st.caption("Complete tasks to earn your first badge.")
    if st.button("Demo: fill the previous 4 days of routine"):
        for d in range(max(0, day - 4), day):
            for cid in rt.CORE + ["meal"]: db.add_task(name, d, cid)
        st.rerun()
    st.caption("Points double when a task matters most. There are no penalties for missed days: the goal is useful data, not perfection.")

# ---------- Learn ----------
with T["Learn"]:
    st.subheader("How to read AstroCare")
    st.write("Every score compares you with **your own normal**, learned from your first 21 days. It is not a population average. A score drops when several indicators move the wrong way together.")
    for c, r, m in COLORS: st.markdown(f":{BADGE[c]}-badge[{c.title()}, {r}] {m}")
    st.subheader("What each indicator means")
    for sg, meta in SIGNALS.items():
        with st.expander(meta["label"]):
            gd_ = GUIDE[sg]; st.write(f"**What:** {gd_['what']}"); st.write(f"**How to measure:** {gd_['how']}"); st.write(f"**Why it matters:** {gd_['why']}")
    st.subheader("The five hazards in plain words")
    for h, (nm, url) in HAZARDS.items(): st.markdown(f"**[{nm}]({url})**: {HAZARD_PLAIN[h]}")
    st.subheader("When to call the ground")
    st.write("If an area is red, or the app says to discuss with the flight surgeon, send the Earth packet and wait for the reply. This tool supports your decisions. It does not diagnose.")

# ---------- Self-check ----------
with T["Self-check"]:
    st.write("Measure, enter, and get an instant read-out with what to do. These are general adult reference ranges; the mission medical protocol and the flight surgeon always come first.")
    with st.expander("Which measurements, and why?"):
        for k, m in sc.INFO.items():
            st.markdown(f"**{m['label']}** ({m['unit']}). **How:** {m['measure']} **Why:** {m['why']} **In space:** {m['space']} Hazard: {hz_link(m['hazard'])}")
    sym = st.checkbox("I have chest pain, trouble breathing, fainting, confusion, severe weakness, or thoughts of harming myself or others")
    sv1, sv2 = st.columns(2)
    vis = sv1.checkbox("Blurred or changed vision"); diz = sv2.checkbox("Dizziness or poor coordination")
    if vis or diz:
        st.warning("Report this to the flight surgeon today. Eye and balance changes can follow spaceflight (NASA risks: SANS; altered sensorimotor and vestibular function). Avoid demanding tasks such as driving a rover until cleared.")
    c1_ = st.columns(4)
    sys_ = c1_[0].number_input("Systolic (mmHg)", 60, 260, int(round(row.bp_sys))); dia_ = c1_[1].number_input("Diastolic (mmHg)", 30, 160, int(round(row.bp_sys * .65)))
    hr_ = c1_[2].number_input("Resting heart rate (bpm)", 25, 220, int(round(row.rhr))); temp_ = c1_[3].number_input("Temperature (°C)", 30.0, 43.0, float(round(row.temp, 1)), 0.1)
    c2_ = st.columns(4)
    glu_ = c2_[0].number_input("Blood glucose (mg/dL)", 20, 600, int(round(row.glucose))); fast_ = c2_[1].toggle("Fasted 8 h", True)
    slp_ = c2_[2].number_input("Sleep last night (h)", 0.0, 14.0, float(round(row.sleep_h, 1)), 0.1); mood_ = c2_[3].slider("Mood (0-10)", 0, 10, int(round(row.mood)), key="sc_mood")
    reads = dict(bp=(sys_, dia_), hr=hr_, glucose=(glu_, fast_), temp=temp_, sleep=slp_, mood=mood_)
    res = sc.assess(reads)
    if sym or any(r["urgent"] for r in res.values()):
        st.error("EMERGENCY: alert a crewmate and the ground team now and follow the mission emergency procedure.")
    elif any(r["status"] == "red" for r in res.values()):
        st.warning("At least one result needs the flight surgeon's attention. See the details below and send the Earth packet.")
    elif any(r["status"] == "amber" for r in res.values()):
        st.info("Some results are outside the usual range. Follow the suggestions and measure again.")
    else:
        st.success("All results are in the normal range.")
    base = {"bp": ("bp_sys", sys_, "mmHg"), "glucose": ("glucose", glu_, "mg/dL"), "temp": ("temp", temp_, "°C"), "hr": ("rhr", hr_, "bpm"), "sleep": ("sleep_h", slp_, "h"), "mood": ("mood", mood_, "/10")}
    cols_ = st.columns(3)
    for i, (k, r) in enumerate(res.items()):
        m = sc.INFO[k]
        with cols_[i % 3].container(border=True):
            lab = {"green": "Normal", "amber": "Watch", "red": "Act now"}[r["status"]]
            st.markdown(f"**{m['label']}** :{BADGE[r['status']]}-badge[{lab}]")
            st.write(r["meaning"])
            if k in base:
                sg, v, u = base[k]; z_ = (v - mu[sg]) / sd[sg]
                st.caption(f"Your baseline: {mu[sg]:.1f} {u}." + (" Normal range, but unusual for you." if r["status"] == "green" and abs(z_) >= 2 else ""))
            for x in r["do"]: st.markdown("- " + x)
            if r["prevent"]: st.caption("Prevent: " + " ".join(r["prevent"]))
            if r["call"]: st.caption("Contact the ground: " + r["call"])
            st.caption("Hazard: " + hz_link(m["hazard"]))
    b1, b2 = st.columns(2)
    if b1.button("Save today's reading"):
        db.add_selfcheck(name, {"day": day, "sys": sys_, "dia": dia_, "hr": hr_, "glucose": glu_, "fasting": fast_, "temp": temp_, "sleep": slp_, "mood": mood_}); st.rerun()
    if b2.button("Demo: add 10 days of sample readings"):
        for d_ in sc.demo_readings(day): db.add_selfcheck(name, d_)
        st.rerun()
    hist = pd.DataFrame(db.selfchecks(name))
    if len(hist):
        pick_k = st.selectbox("History", list(sc.INFO), format_func=lambda x: sc.INFO[x]["label"], key="sc_hist")
        cols_map = {"bp": ["sys", "dia"], "hr": ["hr"], "glucose": ["glucose"], "temp": ["temp"], "sleep": ["sleep"], "mood": ["mood"]}[pick_k]
        fig = go.Figure()
        for cc in cols_map: fig.add_trace(go.Scatter(x=hist.day, y=hist[cc], mode="lines+markers", name=cc))
        if pick_k != "bp": fig.add_hrect(y0=sc.BANDS[pick_k][0], y1=sc.BANDS[pick_k][1], fillcolor="green", opacity=.12, line_width=0)
        else: fig.add_hrect(y0=90, y1=119, fillcolor="green", opacity=.12, line_width=0)
        fig.update_layout(height=280, xaxis_title="mission day", margin=dict(l=10, r=10, t=10, b=10)); st.plotly_chart(fig, width="stretch")
        st.caption("Green band = usual reference range. Sample readings are simulated.")

# ---------- Real NASA data ----------
with T["Real NASA data"]:
    st.markdown("**Real NASA data:** NASA Open Science Data Repository, study **OSD-575** (SpaceX Inspiration4 blood serum metabolic panel and immune/cardiac cytokine arrays). "
                "Table used: `LSDS-8_Comprehensive_Metabolic_Panel_CMP_TRANSFORMED.csv` (4 crew, 7 blood draws each, serum tested by Quest Diagnostics). DOI 10.26030/mc5d-p710, licence CC0 1.0.")
    cmp_ = load_cmp(); an_ = cmp_[["analyte", "label", "unit"]].drop_duplicates("analyte").set_index("analyte")
    names_ = list(an_.index)
    pick_a = st.selectbox("Blood marker", names_, index=names_.index("glucose"), format_func=lambda x: f"{an_.label[x]} ({an_.unit[x]})")
    sb = cmp_[cmp_.analyte == pick_a]; unit_ = sb.unit.iloc[0]; lab_ = sb.label.iloc[0]
    pre = sb[sb.tp.isin(TP_ORDER[:3])].groupby("crew").value.mean(); r1 = sb[sb.tp == "R+1"].set_index("crew").value
    chg = ((r1 - pre) / pre * 100).dropna()
    if len(chg):
        k1, k2, k3 = st.columns(3)
        k1.metric(f"{lab_}: change 1 day after return", f"{chg.mean():+.0f}% on average", f"range {chg.min():+.0f}% to {chg.max():+.0f}%", delta_color="off")
        out_ = int(((sb.value < sb.rmin) | (sb.value > sb.rmax)).sum()); k2.metric("Samples outside the lab's own reference range", f"{out_} of {int(sb.value.notna().sum())}")
        k3.metric("Crew / blood draws", f"{sb.crew.nunique()} / {sb.tp.nunique()}")
    SEX = {"C001": "male", "C002": "female", "C003": "female", "C004": "male"}
    crews = sorted(sb.crew.unique()); fig = make_subplots(rows=2, cols=2, subplot_titles=[f"{c} ({SEX.get(c, '?')})" for c in crews], vertical_spacing=.18)
    for i, cr in enumerate(crews):
        r_, c_ = i // 2 + 1, i % 2 + 1; d_ = sb[sb.crew == cr].sort_values("order")
        if d_.rmin.notna().any() and d_.rmax.notna().any():
            fig.add_hrect(y0=d_.rmin.iloc[0], y1=d_.rmax.iloc[0], fillcolor="green", opacity=.12, line_width=0, row=r_, col=c_)
        fig.add_trace(go.Scatter(x=d_.order, y=d_.value, mode="lines+markers", showlegend=False), row=r_, col=c_)
        fig.add_vline(x=2.5, line_dash="dot", row=r_, col=c_)
        fig.update_xaxes(tickvals=list(range(7)), ticktext=TP_ORDER, row=r_, col=c_)
    fig.update_layout(height=520, margin=dict(l=10, r=10, t=40, b=10), title=f"{lab_} ({unit_}) per crew member")
    st.plotly_chart(fig, width="stretch", key="nasa_cmp")
    st.caption("L-92 means 92 days before launch, R+1 means 1 day after return. Dotted line = the 3-day flight (no in-flight sample in this table). Green band = the lab's reference range stored in the file; it can differ by sex.")
    tbl = pd.DataFrame({"Pre-flight mean": pre.round(1), "1 day after return": r1, "Change %": ((r1 - pre) / pre * 100).round(0)}).dropna()
    st.dataframe(tbl)
    if pick_a == "glucose":
        st.info("Glucose was higher one day after return than each astronaut's own pre-flight average in all four crew members. "
                "Three crew members then have unusually low values at day R+45, which the file does not explain; we show them as recorded and do not interpret them.")
        st.caption("The lab's glucose reference range in this file is 65 to 99 mg/dL. AstroCare's Self-check uses 70 to 99 mg/dL for fasting values.")
    st.markdown("**How AstroCare uses it:** this real data supports treating blood glucose as an indicator that can move in both directions around a personal baseline, which is how the drift engine treats it. "
                "It is evidence for the design, not a clinical result.")
    st.warning("Four de-identified crew members and a 3-day flight: a very small sample. Do not draw clinical conclusions, and do not try to identify individuals. Crew codes are NASA's.")
