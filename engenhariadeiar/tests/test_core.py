import math
from sentinela.core import Simulator

def test_baseline():
    s = Simulator()
    for _ in range(50):
        v = s.step()
    assert v.speed > 40
    assert len(s.history) == 50

def test_event_capture():
    s = Simulator()
    for _ in range(30): s.step()
    for _ in range(30): s.step(fault="Sobrecarga mecânica")
    assert len(s.events) == 1
    assert len(s.events[0]["pre"]) == 25
    assert len(s.events[0]["post"]) == 25

def test_comms():
    s = Simulator()
    v = s.step(fault="Perda de comunicação")
    assert math.isnan(v.speed)
    assert "Comunicação" in v.diagnosis
