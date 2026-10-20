from sentinela.catalog import MACHINES, diagnose
from sentinela.visual import model

def test_all_machines_have_components():
    assert len(MACHINES)==4
    assert all(x['components'] and x['symptoms'] for x in MACHINES.values())
def test_diagnosis():
    a=diagnose('Motor elétrico','Rolamentos',['Vibração excessiva'])
    assert len(a)==1 and 'Desbalanceamento' in a[0]['hypotheses']
def test_invalid_component():
    import pytest
    with pytest.raises(ValueError):diagnose('Motor elétrico','Rotor',['Vibração excessiva'])
def test_models():
    for name in MACHINES: assert len(model(name).data)>0
