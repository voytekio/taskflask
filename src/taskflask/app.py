#!flask/bin/python
import random
from subprocess import Popen, PIPE
import shlex

from flask import Flask, jsonify, abort, make_response, request

app = Flask(__name__)

tasks = [
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
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
def create_task():
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

def run_cmd(cmd_name, debug=False):
    print('running cmd: {}'.format(cmd_name))
    cmdplus = shlex.split(cmd_name)
    process = Popen(cmdplus, stdout=PIPE)
    cmdoutput = process.communicate()
    exit_code = process.wait()
    #random_jid = random.choice(range(1000000))
    return cmdoutput[0]
    
def retrieve_job(jid):
    res = run_cmd('salt-run jobs.lookup_jid {} --out=json'.format(jid))
    if not res:
        return False
    else:
        return res

@app.route('/todo/api/v1.0/jobs/<int:jid>', methods=['GET'])
def get_job(jid):
    result = retrieve_job(jid)
    if not result:
        abort(404)
    return jsonify({'job': result})

@app.route('/todo/api/v1.0/jobs', methods=['POST'])
def create_job():
    if not request.json or not 'command' in request.json:
        abort(400)
    job = {
        'command': request.json['command'],
        'target': request.json.get('target', "'*'"),
        'status': 'new',
        #'title': request.json['title'],
        #'description': request.json.get('description', ''),
        #'done': False
    }
    jid = run_cmd('salt --async {} {} --out=json'.format(job['target'], job['command']))
    job['jid'] = jid
    return jsonify({'job': job}), 201


if __name__ == '__main__':
    app.run(debug=True)
