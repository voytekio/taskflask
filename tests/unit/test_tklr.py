import pytest
import pdb
import mock

#pdb.set_trace()
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

@pytest.fixture()
def sample_file_contents():
    return ['========== INs', 'attempt 1: (started 05/04/19)', '    ==', '    IN::: incoming::: inbound::: ins::', '        ==  ', "        devx.vim. inside cdks's vimrc:", '', '    ==', '    ICEBOX:: (priority V:::)', '        - monthly bills automate: ', '', '========== projects', '==========', 'PJs:: projects:: pj::: pjs::', '', '=====', 'tech:::', '    ==', '    tech.testing::', '        - how to teach pylint to notice iteritems (and ignore six.iteritems) ? ns. rand. ', '========== e.of pjs:: pj::', '', '========== calendar', '=============================================================================', '    ==', '    01:  () ', '        - ALWAYS: monthly', '        pj.gtd. monthly.spinoff(copy this task) - clean days first - sat,mon,thu tags etc.', '', '    ==', '    09: (sat)', '    today:: tdy:: tday:: tdy; tday;    ', '', '    DONEs:: dones; done::', '        ==', '        DONE: - pj.fun. 1. stack overflow and 2. c64 and atari shirts. (BDEAD)', '    ==', '    10: ()', '        - REPEAT. change contacts. ', '            11/10 - both', '    ==', '    31: ()', '        buy: 9v battery (fire alarm)', '', '    ==', '    M12:', "        - (REPEAT.3.months.mar/jun/sept/dec) - check w/ justin if haven't heard. ", '            see keyppl section for last convo date. ', '    ==', '    - Tags::: tag::: ', '        see in journal. ', '', '== e.of tklr']

@pytest.fixture()
def sample_subsections():
    return [('IN', 4, 8, '    IN::: incoming::: inbound::: ins::'), ('ICEBOX', 9, 13, '    ICEBOX:: (priority V:::)'), ('PJs', 14, 16, 'PJs:: projects:: pj::: pjs::'), ('tech', 17, 25, 'tech:::'), ('01', 26, 30, '    01:  () '), ('09', 31, 37, '    09: (sat)'), ('10', 38, 41, '    10: ()'), ('31', 42, 45, '    31: ()'), ('M12', 46, 49, '    M12:'), ('- Tags', 50, 53, '    - Tags::: tag::: ')]

@pytest.fixture()
def sample_sections():
    return [('INs', 1, 11, '========== INs'), ('projects', 12, 22, '========== projects'), ('calendar', 23, 53, '========== calendar')]

'''
@pytest.fixture(tmpdir, sample_contents)
def tklr_file_fixture(file_name):
    pdb.set_trace()
    tklr_file = tmpdir.join('file_name')
    with file.open(tklr_file) as f:
        f.write(sample_contents)

def test_read_file(tmpdir):
    pdb.set_trace()
    t3 = tklrlib.Tklr('foo_file_name')
    t3.read_file('foo_file_name')
'''

@pytest.mark.parametrize('list_to_update, section_name, start, end, expected_tuple, expected_len', [
    ('subsections', 'calendar', 23, 53, ('10', 38, 41, '    10: ()'), 6),
    ('sections', 'major_sections', 0, None, ('projects', 12, 22, '========== projects'), 3),
    ])
def test_find_sections(mocker, sample_file_contents, list_to_update, section_name, start, end, expected_tuple, expected_len):
    # given
    m2 = mock.Mock()
    t2 = tklrlib.Tklr('foo_file_name')
    t2.file_contents = sample_file_contents
    #pdb.set_trace()
    list_attr = getattr(t2, list_to_update)
    tag_attr = t2.searchtags[section_name]['tag']
    ignore_attr = t2.searchtags[section_name]['ignore']
    regex_attr = t2.searchtags[section_name]['regex']
    # when
    res = t2.find_sections(list_attr, tag_attr, ignore_attr, regex_attr, start, end)
    #pdb.set_trace()
    assert expected_tuple in list_attr
    assert expected_len == len(list_attr)

def test_load_full_dict(mocker, sample_sections, sample_subsections, sample_file_contents):
    # given
    m1 = mock.Mock()
    #pdb.set_trace()
    t1 = tklrlib.Tklr('foo_file_name')
    t1.sections = sample_sections
    t1.subsections = sample_subsections
    t1.file_contents = sample_file_contents
    t1.find_sections = m1
    # when:
    res = t1.load_full_dict()
    # then:
    #pdb.set_trace()
    assert len(t1.dict) == 10 # ensure we found 10 subsections
    assert t1.dict['IN']['heading'] == '    IN::: incoming::: inbound::: ins::' # ensure we grab proper headings
    assert '    DONEs:: dones; done::' in t1.dict['09']['contents'] # ensure we grab proper contents

    # below, test how we are calling the file_sections method, since that was a problem before
    # first we test the first call - the one for major sections and look at what Tag we requested
    assert m1.mock_calls[0][1][1] == '========== '
    # then we test the third call ([2]) - to one of the subsections (projects) and look at the regex ([3]) is
    assert m1.mock_calls[2][1][3] == r'\S'


@pytest.mark.parametrize('keyword,expected_res', [('BDEAD:: BRAINDEAD::', True), ('THIS IS SPAM', False)])
def test_match_keyword(keyword, expected_res):
    # given:
    tklr = tklrlib.Tklr('foo_file')
    # when:
    res = tklr.match_keyword(keyword)
    # then:
    assert res == expected_res

