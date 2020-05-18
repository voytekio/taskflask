import shlex
from subprocess import check_output, CalledProcessError

def run_cmd(cmd):
    cmd_plus = shlex.split(cmd)
    try:
        std_out = check_output(cmd_plus)
    except CalledProcessError as e:
        return 'CalledProcessError while running cmd'
    except OSError as e:
        return 'OSError while running cmd'
    return std_out

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

def test_move_today():
    # given
    # ? copy test input file ? 
    # when
    res = run_cmd('taskcmd -f <foo.txt> -t')
    # then
    # read file and look for signs of moved day
    assert 'nope' in 'finish this test'

