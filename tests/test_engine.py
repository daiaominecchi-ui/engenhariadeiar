from sentinela.engine import Twin,SCENARIOS
from sentinela.reporting import pdf_report

def test_all_scenarios_run():
    for scenario in SCENARIOS:
        t=Twin(seed=2);t.set_scenario(scenario);t.run(120)
        assert len(t.history)==120
        assert all(r['speed_rpm']>=0 for r in t.history)

def test_repeatable():
    a=Twin(seed=5);b=Twin(seed=5)
    assert a.run(20)==b.run(20)

def test_events_and_pdf():
    t=Twin();t.run(60);t.set_scenario('Ruído no sensor');t.run(100)
    assert any('Ruído' in e['diagnosis'] for e in t.events)
    assert pdf_report(t).startswith(b'%PDF')

def test_invalid_scenario():
    t=Twin()
    try: t.set_scenario('X')
    except ValueError: return
    assert False
