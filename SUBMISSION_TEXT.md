Project Name

AstroCare Copilot

High-Level Project Summary

AstroCare Copilot is an offline health assistant for astronauts on deep-space missions. It learns each astronaut's personal baseline, detects early drift across six areas (cardiovascular, bone and muscle, immunity and sleep, metabolic and nutrition, mental and social, radiation), explains every alert in plain words, and recommends concrete actions. Because Mars is up to about 20 minutes away by radio, the crew must be medically autonomous: AstroCare runs entirely on board and prepares a compact, prioritised packet for the ground team. It follows NASA's five hazards of human spaceflight, and the same approach can support remote and polar communities on Earth.

Link to Project Demo

https://github.com/khadija12-tech/astrocare-copilot/blob/main/demo/AstroCare_Demo_Deck.pdf

Link to Final Project

https://khadija12-tech.github.io/astrocare-copilot/

Detailed Project Description

What it does: for each astronaut it compares daily signals (resting heart rate, heart-rate variability, sleep, mood, fatigue, exercise, voice, social time, immune stress marker, radiation dose rate) with that astronaut's own baseline, not a population average. A drift score and an Isolation Forest flag unusual combinations early, including blood pressure, blood glucose and body temperature (a scripted simulated fever is caught early). Each alert says why (for example "Resting heart rate +11% vs baseline (last 5 days)") and is tagged with the related NASA hazard.

How it works: Python (pandas, scikit-learn) computes baselines, z-score drift, Isolation Forest anomalies and system scores; rule-based recommendations are re-ranked from crew feedback stored in a local SQLite database, so everything works offline. A 30-day digital twin compares "no change" with "follow the plan". A crew-dynamics view shows pairwise tension and isolation. A voice module measures pitch variability, speech rate and pauses locally (raw audio is discarded). Delay mode builds a compact priority packet queued for Earth. The interface is a Streamlit app, plus a WebXR habitat view (A-Frame) and an offline mobile web app (PWA) for check-ins and the daily routine. It adapts to four environments (spacecraft in transit, space station, lunar base, Mars base or rover), including gravity and radio-delay differences. A Self-check tab lets the astronaut enter blood pressure, resting heart rate, blood glucose, body temperature, sleep and mood, then shows an instant colour-coded read-out against general adult reference ranges, what to do now, how to prevent worsening, when to contact the ground, why the measurement matters and how spaceflight hazards affect it; urgent symptoms trigger an emergency message and the result is added to the Earth packet. A daily routine prompts the measurements that matter most and raises priority when an area is drifting; a gentle points, streak and badge system (no penalties) encourages the routine. Colour-coded status (green, amber, red), dynamic charts with mission-day replay, and a plain-language Learn tab explain every indicator, how to measure it and why it matters, so astronauts do not need prior health expertise.

Benefits: earlier warning, explainable decisions for a tired crew, low cognitive load (traffic-light view), privacy (data stays on board).

Limits: decision support, not a medical diagnosis; reference ranges are general adult values and must be reviewed by a clinician, and mission medical protocols always take priority. The demo data is SIMULATED, and rules and thresholds are illustrative and need validation by flight surgeons. In 30 simulated seeds, about 3% of healthy-crew system-days were flagged amber or red (false alarms).

Tools: Python, pandas, scikit-learn, NumPy, Plotly, Streamlit, SQLite, A-Frame (WebXR), HTML/JavaScript PWA.

Links: live app https://astrocare-copilot-neus8cerqkh83r6pkm3jak.streamlit.app/ | landing page with VR habitat and mobile app https://khadija12-tech.github.io/astrocare-copilot/ | source code https://github.com/khadija12-tech/astrocare-copilot

Use of Super Intelligence (SI)

Yes. Claude (Anthropic) was used to generate code scaffolding (Python modules, Streamlit app, WebXR and PWA pages) and draft text, all reviewed and edited by the team. The project idea, scope and design decisions are the team's own. Source files carry an "AI-assisted" header. The demo voice is synthesized by code, not by an SI audio model. No images, video or audio were generated with SI; the images in the demo deck are screenshots of our own app and charts drawn from our own data.

NASA Data

NASA Human Research Program (HRP) resources, used to decide the structure, indicators and environments of the tool:

- "5 Hazards of Human Spaceflight" (nasa.gov/hrp/hazards): the whole system is organised around the five hazards (space radiation, isolation and confinement, distance from Earth, gravity fields, hostile/closed environments), and every alert and recommendation is tagged with its hazard. The hazards overview also says the hazards feed off one another, which is why AstroCare shows stress, sleep and immunity together.

- NASA "Analog Missions" (nasa.gov/analog-missions) and the analog pages it links (HERA, CHAPEA, Antarctic stations, :envihab, ARGOS, NASA Space Radiation Laboratory): used to understand how isolation, reduced gravity and radiation affect health, and to choose the environments the tool supports (spacecraft in transit, space station, lunar base, Mars base or rover).

- "Risks of Human Spaceflight" (nasa.gov/hrp/risks): used to choose the health indicators and to check coverage. The app includes a table mapping 17 NASA human-system risks to what AstroCare does: 6 covered (immune, cardiovascular, fitness, behavioral health, teamwork, sleep), 6 partly (bone, nutrition, host-microorganism, SANS, sensorimotor and vestibular, radiation) and 5 openly out of scope (decompression sickness, hypoxia, spacewalk injury, systems operations, dynamic loads).

- NASA Open Science Data Repository (OSDR), study OSD-575, "SpaceX Inspiration4 Blood Serum Metabolic Panel and Immune/Cardiac Cytokine Arrays": we used the Comprehensive Metabolic Panel table (LSDS-8_Comprehensive_Metabolic_Panel_CMP_TRANSFORMED.csv, 4 crew members, 7 blood draws each from 92 days before launch to 194 days after return) in a "Real NASA data" tab. It shows how blood markers changed from each astronaut's own pre-flight baseline. For example, serum glucose was higher one day after return than each astronaut's pre-flight average in all four crew members (+14% to +44%, mean +24%). This real data supports treating glucose as an indicator that can move in both directions around a personal baseline, as our drift engine does. It is design evidence, not a clinical result: the sample is four de-identified crew members and a 3-day flight, and the table has no in-flight sample. Study DOI 10.26030/mc5d-p710, licence CC0 1.0; the metabolic panel was run by Quest Diagnostics.

- NASA HRP "Ongoing HRP Research in Space" / Human Investigations (Artemis II, low Earth orbit and past studies): used to choose and justify indicators and features: ARCHeR (wrist actigraphy of motion, sleep and light exposure) for the sleep and activity signals; Standard Measures and Artemis II Standard Measures for using one consistent set of physiological and psychological indicators; Artemis II Immune Biomarkers and Altered Immunity for the immune stress and temperature indicators; the SANS studies (B-Complex, Brain Fluid Pressure, Thigh Cuff, Spinal Fluid Biomarkers) for the vision-change prompt; Food Acceptability and Food Physiology for nutrition reminders; Zero T2 and Spinal Health for the exercise routine; and Tempus Pro (telemedicine device integrating health data for remote, near real-time review) for the compact Earth packet.

The daily crew time series in the demo are simulated; the OSD-575 data is the only real NASA measurement data used.

Space Agency Partner Data and Other References

Space Agency Partner resource: Canadian Space Agency (CSA), "Monitoring Radiation for Astronaut Health" (asc-csa.gc.ca, 26 Feb 2026). It describes the Canadian Active Neutron Spectrometer (CANS), a compact instrument that measures neutron radiation exposure continuously and autonomously, and notes that neutron radiation contributes about 30% of total radiation on the ISS. We used it to design the radiation part of AstroCare: a continuous dose-rate signal read from a dosimeter, a cumulative dose view, and shelter-and-report guidance when the rate rises.

Publications linked on the NASA OSDR OSD-575 study page, read for background on the Inspiration4 data we used:
- Overbey et al., "The Space Omics and Medical Atlas (SOMA) and international astronaut biobank", Nature (2024), DOI 10.1038/s41586-024-07639-y.
- Overbey et al., "Collection of Biospecimens from the Inspiration4 Mission Establishes the Standards for the Space Omics and Medical Atlas (SOMA)", Nature Communications (2024), DOI 10.1038/s41467-024-48806-z.

Software: Python, pandas, NumPy, scikit-learn, Plotly, Streamlit, SQLite, A-Frame, plus Python and JavaScript standard libraries. All other code is original (AI-assisted, see the SI section).

NASA OSDR study OSD-575 (DOI 10.26030/mc5d-p710, licence CC0 1.0) is cited in the NASA Data section.
