# app/risk_engine.py
RISK_LEVEL_SAFE = "safe"
RISK_LEVEL_SUSPICIOUS = "suspicious"
RISK_LEVEL_CRITICAL = "critical"

def _clamp(x, lo=0, hi=100):
    return max(lo, min(hi, x))

def calculate_risk(packet, history):
    """
    packet: RiskDataPacket benzeri (ip_address, device_info, login_time alanları olmalı)
    history: dict { known_ips:set, known_devices:set, failed_last_10min:int }
    """
    risk = 0
    reasons = []

    if history.get("known_ips") and packet.ip_address not in history["known_ips"]:
        risk += 20
        reasons.append("new_ip")

    if history.get("known_devices") and packet.device_info not in history["known_devices"]:
        risk += 30
        reasons.append("new_device")

    hour = packet.login_time.hour
    if hour in [0, 1, 2, 3, 4]:
        risk += 10
        reasons.append("odd_hour")

    if history.get("failed_last_10min", 0) >= 3:
        risk += 25
        reasons.append("rapid_failures")

    return _clamp(risk), reasons

def calculate_trust(current_trust, risk, success: bool):
    trust = float(current_trust or 0.0)
    if success:
        trust += 5
        trust -= (risk * 0.10)
    else:
        trust -= 8
        trust -= (risk * 0.15)
    return float(_clamp(trust, 0, 100))

def decide_action(risk, trust):
    if risk >= 70 or (risk >= 60 and trust < 40):
        return "DECOY", RISK_LEVEL_CRITICAL
    if risk >= 40:
        return "MFA", RISK_LEVEL_SUSPICIOUS
    return "SAFE", RISK_LEVEL_SAFE
