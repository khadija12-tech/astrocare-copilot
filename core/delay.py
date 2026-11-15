"""Communication-delay mode: compact, prioritised packet queued on board and sent to Earth."""
import json

def build_packet(name, day, scores, overall, items, recs, escalate):
    pr = "URGENT" if escalate else ("WATCH" if items else "ROUTINE")
    return {"v": 1, "crew": name, "day": int(day), "priority": pr,
            "scores": {k: int(v) for k, v in scores.items()}, "overall": int(overall),
            "drivers": [{"s": i["signal"], "z": i["harm_z"]} for i in items[:4]],
            "recs": [r["id"] for r in recs[:3]], "ask_ground": bool(escalate)}

def packet_bytes(pkt):
    return len(json.dumps(pkt, separators=(",", ":")).encode())

def timeline(delay_min, review_min=30):
    return [("T+0 min", "Packet queued on board (works offline, no link needed)"),
            (f"T+{delay_min} min", "Packet arrives at Mission Control"),
            (f"T+{delay_min + review_min} min", "Flight surgeon reviews the prioritised alert"),
            (f"T+{2 * delay_min + review_min} min", "Ground reply arrives on board")]
