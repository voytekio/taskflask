import pytest
import pdb
import mock

#pdb.set_trace()
import taskflask.tklr as tklr_lib

def test_find_sections():
    # given
    tklr_obj = tklr_lib.Tklr(filename='tests/assets/sections.txt', no_save=True, debug=False)
    # when
    ret = tklr_obj.find_sections(tag = '========== ', ignore_string = 'e.of', regex = '========== ', start = 0, end=None)
    # then
    assert len(ret) == 2 # we found 2 sections
    assert 'ONLINE_SHOPPING_LIST' in ret[1][0] # we have correct in tag_name
    assert ret[0][2] == 6 # we found end of section to be 1 line before the next section
    assert ret[1][2] == 16 # we found end to be last line if there was no more sections

def test_load_full_dict():
    # given
    tklr_obj = tklr_lib.Tklr(filename='tests/assets/sections.txt', no_save=True, debug=False)
    tklr_obj.searchtags['GROCERY_LIST_LINE_1'] = {
        'tag':'    ',
        'ignore': '==',
        'regex': r'    \S',
    }
    tklr_obj.searchtags['ONLINE_SHOPPING_LIST_LINE_7'] = {
        'tag':'    ',
        'ignore': '==',
        'regex': r'    \S',
    }
    # when
    tklr_obj.load_full_dict()
    # then
    assert len(tklr_obj.dict) == 4 # we have 2 major and 2 minor sections
    assert len(tklr_obj.subsections) == 4 # same as above but in the subsections list
    assert 'walmart' in tklr_obj.dict.keys() # we have a walmart minor section
    assert 'amazon' not in tklr_obj.dict.keys() # amazon should not be a heading
        # since it doesn't match the filter
    assert len(tklr_obj.dict['cart']['contents']) == 3 # we should have 3 lines in
        #amazon subsection - bar, baz and last line 16


def test_load_into_dict():
    # given
    tklr_obj = tklr_lib.Tklr(filename='tests/assets/sections.txt', no_save=True, debug=False)
    tklr_obj.subsections.append(tklr_lib.Section_Tuple_Class(name='cart', start=13, end=16, full_name='    cart:'))
    # when
    tklr_obj.load_into_dict()
    # then
    assert len(tklr_obj.dict) == 1
    assert 'cart:' in tklr_obj.dict['cart']['heading']
    assert '        - last line 16' in tklr_obj.dict['cart']['contents']

