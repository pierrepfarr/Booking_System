import sys
import pytest

sys.path.append('../src/classes')
from interface import Interface

interface = Interface()

@pytest.mark.parametrize('trial',["100","2000","24000"])
def test_check_funds(trial):
    assert interface.check_funds(trial)

@pytest.mark.parametrize('trial',["100.5","0","25001"])
def test_invalid_check_funds(trial):
    assert not interface.check_funds(trial)

@pytest.mark.parametrize('trial',['high velocity crusher','polymer extruder2','irradiator1'])
def test_check_request(trial):
    assert interface.check_request(trial)

@pytest.mark.parametrize('trial',["shop5","test","saw"])
def test_invalid_check_request(trial):
    assert not interface.check_request(trial)

@pytest.mark.parametrize('trial',["13:00","01:30","15:30"])
def test_check_time(trial):
    assert interface.check_time(trial)

@pytest.mark.parametrize('trial',["16:20","52:00","13:32"])
def test_invalid_check_time(trial):
    assert not interface.check_time(trial)

@pytest.mark.parametrize('trial',["2021-09-08","2021-12-01","1995-01-01"])
def test_check_date(trial):
    assert interface.check_date(trial)

@pytest.mark.parametrize('trial',["2021-32-05","2021-05-32","04-05-2020"])
def test_invalid_check_date(trial):
    assert not interface.check_date(trial)

@pytest.mark.parametrize('trial',['client','admin'])
def test_check_role(trial):
    assert interface.check_role(trial)

@pytest.mark.parametrize('trial',["shopper","booker","10"])
def test_invalid_check_role(trial):
    assert not interface.check_role(trial)