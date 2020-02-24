import pytest
import subprocess
import shlex
import pdb
import os
import time

def run_cmd(cmdname, ignore_errors=False):
    import subprocess
    import shlex

    cmd_to_run = shlex.split(cmdname)
    try:
        res = subprocess.check_output(cmd_to_run, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        print('ERROR: failure running cmd: "{}".\nError: {}'.format(cmdname, err.output))
    except OSError as err:
        print('ERROR: failure running cmd: "{}".\nError: {}'.format(cmdname, err.strerror))
    else:
        return res
    if ignore_errors:
        return False
    else:
        raise BaseException

        '''
        - docker run (-it) ubuntu(:14.04) /bin/bash (-c "sleep 10") 
            (- i - "Keep STDIN open even if not attached", - t - sudo/pseudo tty)
            -v ~/rand/wheelhouse:/wheels  (-v <source>:<dest>)
            -d -daemonized?
            -p 5001:80 nginx (5001 on host to 80 on CR)
        '''

@pytest.fixture()
def my_fixture():
    print('\nFIXTURE SETUP')
    # obtain docker CR and its ID
    cwd = os.getcwd()
    cr_id = run_cmd( "docker run -i -d -v {}:/task ubuntu:18.04".format(os.path.join(cwd, 'taskflask') ))
    cr_id = cr_id.strip()
    print('cr_id: {}'.format(cr_id))
    print(run_cmd( "docker exec -i {} ls -l /task".format(cr_id)))
    yield cr_id.strip()

    print('\nFXITURE TEARDOWN. destroying CR with ID of {}'.format(cr_id))
    time.sleep(30)
    run_cmd( "docker rm -f {}".format(cr_id))

