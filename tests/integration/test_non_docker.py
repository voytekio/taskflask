import os
import shlex
from shutil import copy
from subprocess import check_output, CalledProcessError

import pytest

def run_cmd(cmd):
    cmd_plus = shlex.split(cmd)
    try:
        std_out = check_output(cmd_plus)
    except CalledProcessError as e:
        return 'CalledProcessError while running cmd'
    except OSError as e:
        return 'OSError while running cmd'
    return std_out

@pytest.fixture()
def copy_asset_files():
    assets_dir = os.path.join(os.getcwd(), 'tests/assets')
    print('ASSETS_DIR: {}'.format(assets_dir))
    assets_files_unfiltered = os.walk(assets_dir).next()[2] #retrieve first iteration - root dir
        # and then its files - [2]
    assets_files = [x for x in assets_files_unfiltered if '.test' not in x]
    for src in assets_files:
        dst = src + '.test'
        try:
            copy(os.path.join(assets_dir, src), os.path.join(assets_dir, dst))
        except:
            print('ERROR copying file {} to {}'.format(src, dst))
            raise
    yield assets_dir
    for src in assets_files:
        dst = src + '.test'
        try:
            os.remove(os.path.join(assets_dir, dst))
        except:
            print('ERROR deleting file {}'.format(dst))
            raise


def test_it_installs():
    # given
    # when
    res = run_cmd('pip list')
    # then
    assert 'taskflaskapi' in res

def test_help_menu():
    # given
    output_tag = '--today'
    # when
    res = run_cmd('taskcmd -h')
    #res = run_cmd('python taskflask/cmdline.py --help') # if you dont have tox/venv, run this instead
    # then
    assert output_tag in res

def test_move_today(copy_asset_files):
    # given
    #copy of the asset file using the copy fixture
    today_sample_file = os.path.join(copy_asset_files, 'today.txt.test')
    # when
    res = run_cmd('taskcmd -f {} -t'.format(today_sample_file))
    # then
    # read file and look for signs of moved day
    with open(today_sample_file) as f:
        whole_file = f.read()
        file_lines = whole_file.split('\n')
    for counter, line in enumerate(file_lines):
        if 'item01' in line:
            item01_index = counter
        elif 'item02' in line:
            item02_index = counter
    assert item01_index - item02_index == 1 # item 01 and 02 are next to each other
    assert 'nope' in 'finish integration test by mocking date with freezegun mod'

