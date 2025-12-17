from datetime import datetime
from types import SimpleNamespace
from app.risk_engine import calculate_risk, decide_action

def test_risk_engine_new_ip_device():
    packet = SimpleNamespace(
        ip_address="2.2.2.2",
        device_info="NEW_DEVICE",
        login_time=datetime.utcnow()
    )
    history = {
        "known_ips": {"1.1.1.1"},
        "known_devices": {"OLD_DEVICE"},
        "failed_last_10min": 0
    }

    risk, reasons = calculate_risk(packet, history)
    assert risk >= 50
    assert "new_ip" in reasons
    assert "new_device" in reasons

def test_decide_action():
    assert decide_action(10, 80)[0] == "SAFE"
    assert decide_action(50, 80)[0] == "MFA"
    assert decide_action(80, 20)[0] == "DECOY"
