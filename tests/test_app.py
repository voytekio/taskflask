import pytest
import taskflask

#@pytest.mark.voytek
def test_101():
    assert 1 == 1

def test_102():
    assert 1 == 1

def test_app_flask(mocker, success_return):
    #mocker.patch('taskflask.app.run_cmd', return_value=success_return)
    mocker.patch('taskflask.app.run_cmd', return_value=323233232)
    #res2 = taskflask.app.run_cmd('foo_cmd')
    res = taskflask.app.retrieve_job(323233232)
    print('res2: {}'.format(res))
    assert res == 323233232

def test_app_flask2(mocker, success_return):
    mocker.patch('taskflask.app.run_cmd', return_value='')
    res = taskflask.app.retrieve_job(323233232)
    print('res2: {}'.format(res))
    assert res == False

'''
def test_3():
    res = taskflask.app.create_salt_job()
    assert res == 'foo'
'''

@pytest.fixture(scope='module')
def success_return():
	return {'status':200}

@pytest.fixture(scope='module')
def failure_return():
	return {'status':404}

'''
def test_foo(mocker)
    mocker.patch(blahblahblah)
        or (to get an object you can introspect and also specify a return value):
    mocked_rhst = mocker.patch('salt.modules.cmdmod.run', return_value='foo')
'''
