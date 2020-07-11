#!flask/bin/python
'''
simple flask file to get started
'''
from __future__ import absolute_import, print_function
from subprocess import Popen, PIPE
import shlex
import pdb  # pylint: disable=unused-import

from flask import Flask, jsonify, abort, make_response, request  # pylint: disable=import-error


app = Flask(__name__)  # pylint: disable=invalid-name

tasks = [  # pylint: disable=invalid-name
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]
@app.errorhandler(404)
def not_found(error):  # pylint: disable=unused-argument
    ''' flask error handler for 404s '''
    return make_response(jsonify({'error': 'Not found'}), 404)


def run_cmd(cmd_name):
    ''' cmd runner that was written too quick '''
    print('USING OLD RUN_CMD, NEED TO REFACTOR THIS')  # pylint: disable=print-statement
    print('running cmd: {}'.format(cmd_name))  # pylint: disable=print-statement
    cmdplus = shlex.split(cmd_name)
    process = Popen(cmdplus, stdout=PIPE)
    cmdoutput = process.communicate()
    #exit_code = process.wait()
    return cmdoutput[0]

def retrieve_job(jid):
    ''' retrieves a salt job given a jid. '''
    res = run_cmd('salt-run jobs.lookup_jid {} --out=json'.format(jid))
    if not res:
        return False
    return res


@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():  # pylint: disable=missing-docstring
    return jsonify({'tasks': tasks})

@app.route('/')
def hello():  # pylint: disable=missing-docstring
    return 'hello world!'

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):  # pylint: disable=missing-docstring
    tasks_filtered = [task for task in tasks if task['id'] == task_id]
    if not tasks_filtered:
        abort(404)
    return jsonify({'task': tasks_filtered[0]})

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():  # pylint: disable=missing-docstring
    if not request.json or not 'title' in request.json:
        abort(400)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ''),
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201


@app.route('/todo/api/v1.0/salt_jobs/<int:jid>', methods=['GET'])
def get_job(jid):  # pylint: disable=missing-docstring
    # example curl:
    # curl -k http://localhost:5000/todo/api/v1.0/salt_jobs/20191109171940356420
    result = retrieve_job(jid)
    if not result:
        abort(404)
    return jsonify({'job': result})

@app.route('/todo/api/v1.0/salt_jobs', methods=['POST'])
def create_salt_job():  # pylint: disable=missing-docstring
    # example curl:
    # curl -k http://localhost:5000/todo/api/v1.0/salt_jobs
      #-X POST -H "Content-Type: application/json"
      #-d '{"command":"test.ping","target":"master3"}'
    if not request.json or not 'command' in request.json:
        abort(400)
    job = {
        'command': request.json['command'],
        'target': request.json.get('target', "'*'"),
        'status': 'new',
    }
    jid = run_cmd('salt --async {} {} --out=json'.format(job['target'], job['command']))
    job['jid'] = jid
    return jsonify({'job': job}), 201
