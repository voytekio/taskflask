import pytest
import pdb

import taskflask.tklr as tklrlib

@pytest.mark.xfail
def test_foo():
    assert 1 == 0

@pytest.mark.smoke
def test_init():
    # given:
    # then: (before when) - we expect a typeerror exception
    with pytest.raises(TypeError):
        # when: we initialize w/o filename
        tklr = tklrlib.Tklr()

def test_match_keyword():
    # given:
    tklr = tklrlib.Tklr('foo_file')
    # when:
    res = tklr.match_keyword('BDEAD:: BRAINDEAD::')
    # then:
    assert res == True

    # when:
    res = tklr.match_keyword('THIS IS SPAM')
    # then:
    assert res == False
