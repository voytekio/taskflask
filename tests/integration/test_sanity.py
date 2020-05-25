from dateutil import tz
import os
import pdb
import shlex
from shutil import copy
from subprocess import check_output, CalledProcessError

from datetime import datetime, timedelta
import pytest

def run_cmd(cmd):
    cmd_plus = shlex.split(cmd)
    try:
        std_out = check_output(cmd_plus)
    except CalledProcessError as e:
        #pdb.set_trace()
        return 'CalledProcessError while running cmd. Error is: \n==================== start error output ====================\n{}.\n==================== end error output ===================='.format(e.output)
    except OSError as e:
        return 'OSError while running cmd. error is: {}'.format(e.strerror)
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
    #pdb.set_trace()

    # given
    # copy of the asset file using the copy fixture
    # and get today and yestrday as day:
    today_sample_file = os.path.join(copy_asset_files, 'today.txt.test')
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')
    today = datetime.now()
    yesterday = today - timedelta(hours=24)
    today = today.replace(tzinfo=from_zone)
    yesterday = yesterday.replace(tzinfo=from_zone)
    today_local = today.astimezone(to_zone)
    yesterday_local = yesterday.astimezone(to_zone)

    # when
    #pdb.set_trace()
    std_out = run_cmd('taskcmd -f {} -t'.format(today_sample_file))
    print('==================== start_normal_cmd_output: ====================\n')
    print(std_out)
    print('==================== end_normal_cmd_output: ====================\n')

    # then
    #pdb.set_trace()
    # read file and look for signs of moved day
    with open(today_sample_file) as f:
        whole_file = f.read()
        file_lines = whole_file.split('\n')
    for counter, line in enumerate(file_lines):
        if 'item{}'.format(today_local.strftime('%d')) in line:
            item_today_index = counter
        elif 'item{}'.format(yesterday_local.strftime('%d')) in line:
            item_yesterday_index = counter
    assert item_yesterday_index - item_today_index == 1 # item from today
    #and yesterdy are next to one another
    #assert 'nope' in 'finish integration test by mocking date with freezegun mod'

