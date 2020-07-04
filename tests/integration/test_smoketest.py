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

@pytest.fixture(scope='module')
def simple_dates():
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/New_York')

    today = datetime.now()
    today = today.replace(tzinfo=from_zone)
    today_local = today.astimezone(to_zone)
    yesterday = today - timedelta(hours=24)
    yesterday = yesterday.replace(tzinfo=from_zone)
    yesterday_local = yesterday.astimezone(to_zone)
    day_before_yesterday = today - timedelta(hours=48)
    day_before_yesterday = day_before_yesterday.replace(tzinfo=from_zone)
    day_before_yesterday_local = day_before_yesterday.astimezone(to_zone)
    tomorrow = today + timedelta(hours=24)
    tomorrow = tomorrow.replace(tzinfo=from_zone)
    tomorrow_local = tomorrow.astimezone(to_zone)
    yield {'today': today_local, 'yesterday': yesterday_local, 'tomorrow': tomorrow_local, 'day_before_yesterday': day_before_yesterday_local}


def test_it_installed():
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

def test_fix_days(copy_asset_files, simple_dates):
    # given
    # copy of the asset file using the copy fixture
    today_sample_file = os.path.join(copy_asset_files, 'today.txt.test')

    # when
    #pdb.set_trace()
    std_out = run_cmd('taskcmd -f {} -a'.format(today_sample_file))
    print('==================== start_normal_cmd_output: ====================\n')
    print(std_out)
    print('==================== end_normal_cmd_output: ====================\n')

    # then
    # read file and look for signs of day names in parenthesis being adjusted
    with open(today_sample_file) as f:
        whole_file = f.read()
        file_lines = whole_file.split('\n')
    line_today = 'today not found'
    # we need another day besides today since the test file has Saturday put in so the test could accidentally
    # work if it was being run on Saturday. Having another day (yesterday or tomorrow) will ensure tests are reliable
    otherday = simple_dates['tomorrow'] if simple_dates['tomorrow'].strftime('%m') == simple_dates['today'].strftime('%m') else simple_dates['yesterday']
    # we pick tomorrow always unless tomorrow belongs to another month which would screw everything up so in that case we pick yesteday
    #pdb.set_trace()
    # %a - 3letter weekday (Sat), %d-day-of-month (15)
    for counter, line in enumerate(file_lines):
        if '{}:'.format(simple_dates['today'].strftime('%d')) in line:
            line_today = line
        if '{}:'.format(otherday.strftime('%d')) in line:
            line_otherday = line
    assert simple_dates['today'].strftime('%a') in line_today
    assert otherday.strftime('%a') in line_otherday

#@pytest.mark.skip(reason='temporary for perf')
def test_move_today(copy_asset_files, simple_dates):
    #pdb.set_trace()

    # given
    # copy of the asset file using the copy fixture
    today_sample_file = os.path.join(copy_asset_files, 'today.txt.test')

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
        if 'item{}'.format(simple_dates['today'].strftime('%d')) in line:
            item_today_index = counter
        elif 'item{}'.format(simple_dates['yesterday'].strftime('%d')) in line:
            item_yesterday_index = counter
    assert item_yesterday_index - item_today_index == 1 # item from today
    #and yesterdy are next to one another

def test_move_today_by_2_days(copy_asset_files, simple_dates):
    #pdb.set_trace()

    # given
    # copy of the asset file using the copy fixture
    today_sample_file = os.path.join(copy_asset_files, 'today.txt.test')

    # when
    #pdb.set_trace()
    std_out = run_cmd('taskcmd -f {} -t -c 2'.format(today_sample_file))
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
        if 'item{}'.format(simple_dates['today'].strftime('%d')) in line:
            item_today_index = counter
        elif 'item{}'.format(simple_dates['yesterday'].strftime('%d')) in line:
            item_yesterday_index = counter
        elif 'item{}'.format(simple_dates['day_before_yesterday'].strftime('%d')) in line:
            item_day_before_yesterday_index = counter
    assert item_yesterday_index - item_today_index == 1 # item from today
    #and yesterdy are next to one another
    assert item_day_before_yesterday_index - item_today_index == 2 # item from today
    #and day_before_yesterday are almost next to one another save for the item_yesterday
    # that's between them
