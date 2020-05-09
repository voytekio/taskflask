import pytest
import pdb
import mock

#pdb.set_trace()
import taskflask.tklr as tklrlib


@pytest.fixture()
def new_fix_section():
    pass

@pytest.fixture()
def new_fix_subsection():
    subsection_text = ''
    filename = 'tests/assets/subsection.txt'
    print('Using file: {}'.format(filename))
    with open(filename) as f:
        for one_line in f:
            subsection_text += one_line
    return subsection_text

@pytest.fixture()
def new_fix_entire_file():
    pass



def test_find_sections(new_fix_subsection):
    print('subsection is:\n{}'.format(new_fix_subsection))
    assert 'DONE' in 'finish the tests'

def test_load_full_dict():
    assert 'DONE' in 'finish the tests'



