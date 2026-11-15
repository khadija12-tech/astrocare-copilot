"""Local SQLite storage: works fully offline."""
import sqlite3, pathlib, contextlib
P = pathlib.Path(__file__).resolve().parent.parent / "data" / "astrocare.db"

def _c():
    P.parent.mkdir(exist_ok=True)
    return contextlib.closing(sqlite3.connect(P))

def init():
    with _c() as c:
        c.executescript("""CREATE TABLE IF NOT EXISTS feedback(rec_id TEXT, helpful INTEGER, ts DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS tasks(astronaut TEXT, day INTEGER, task_id TEXT, UNIQUE(astronaut, day, task_id));
        CREATE TABLE IF NOT EXISTS selfchecks(astronaut TEXT, day INTEGER, sys REAL, dia REAL, hr REAL, glucose REAL, fasting INTEGER, temp REAL, sleep REAL, mood REAL, UNIQUE(astronaut, day));
        CREATE TABLE IF NOT EXISTS checkins(astronaut TEXT, day INTEGER, mood REAL, fatigue REAL, tension REAL, ts DEFAULT CURRENT_TIMESTAMP);""")
        c.commit()

def add_feedback(rec_id, helpful):
    with _c() as c:
        c.execute("INSERT INTO feedback(rec_id,helpful) VALUES(?,?)", (rec_id, int(helpful))); c.commit()

def feedback_stats():
    with _c() as c:
        rows = c.execute("SELECT rec_id, SUM(helpful=1), SUM(helpful=0) FROM feedback GROUP BY rec_id").fetchall()
    return {r[0]: (r[1] or 0, r[2] or 0) for r in rows}

def add_checkin(name, day, mood, fatigue, tension):
    with _c() as c:
        c.execute("INSERT INTO checkins(astronaut,day,mood,fatigue,tension) VALUES(?,?,?,?,?)",
                  (name, int(day), mood, fatigue, tension)); c.commit()

def checkins():
    with _c() as c:
        return c.execute("SELECT astronaut, day, mood, fatigue, tension FROM checkins ORDER BY ts").fetchall()

def add_task(name, day, task_id):
    with _c() as c:
        c.execute("INSERT OR IGNORE INTO tasks(astronaut,day,task_id) VALUES(?,?,?)", (name, int(day), task_id)); c.commit()

def tasks(name):
    with _c() as c:
        return c.execute("SELECT day, task_id FROM tasks WHERE astronaut=?", (name,)).fetchall()

SC_COLS = ["day", "sys", "dia", "hr", "glucose", "fasting", "temp", "sleep", "mood"]

def add_selfcheck(name, d):
    with _c() as c:
        c.execute("INSERT OR REPLACE INTO selfchecks(astronaut,day,sys,dia,hr,glucose,fasting,temp,sleep,mood) VALUES(?,?,?,?,?,?,?,?,?,?)",
                  (name, int(d["day"]), d["sys"], d["dia"], d["hr"], d["glucose"], int(d["fasting"]), d["temp"], d["sleep"], d["mood"])); c.commit()

def selfchecks(name):
    with _c() as c:
        rows = c.execute("SELECT " + ",".join(SC_COLS) + " FROM selfchecks WHERE astronaut=? ORDER BY day", (name,)).fetchall()
    return [dict(zip(SC_COLS, r)) for r in rows]
