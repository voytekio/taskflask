#!flask/bin/python
import random
from collections import OrderedDict
from subprocess import Popen, PIPE
import shlex
import six
import re

from flask import Flask, jsonify, abort, make_response, request

import pdb

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

def foo_func(bar=0):
    return bar * 2

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

@app.route('/')
def hello():
    return 'hello world!'

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


@app.route('/todo/api/v1.0/salt_jobs/<int:jid>', methods=['GET'])
def get_job(jid):
    # example curl:
    # curl -k http://localhost:5000/todo/api/v1.0/salt_jobs/20191109171940356420
    result = retrieve_job(jid)
    if not result:
        abort(404)
    return jsonify({'job': result})

@app.route('/todo/api/v1.0/salt_jobs', methods=['POST'])
def create_salt_job():
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

class Tklr():
    def __init__(self, filename):
        self.sections = []
        self.subsections = []
        self.file_contents = []
        self.filename = filename
        self.dict = OrderedDict()
        self.keywords = [
            'today',
            'DAILY',
            'URGENTs',
            'Awaits',
            'Misc',
            'EVENING',
            'BRAINDEAD',
            'DONEs',
        ]

    def match_keyword(self, line):
        for keyword in self.keywords:
            print('kword: {}, line: {}'.format(keyword, line))
            if keyword in line:
                print('SKIP')
                return True
        return False

    def read_file(self, filename):
        with open(filename) as f:
            for one_line in f:
                self.file_contents.append(one_line.strip('\n'))

    def load_dict(self):
        #pdb.set_trace()
        for one_subsection in self.subsections:
            self.dict[one_subsection[0]] = self.file_contents[one_subsection[1]:one_subsection[2]]
        
    def find_sections(self, list_to_update, tag='========== ', ignore='e.of', regex=r'    \S'):
        if not self.file_contents:
            self.read_file(self.filename)
        for line_counter, one_line in enumerate(self.file_contents):
            if re.match(regex, one_line) and ignore not in one_line and not self.match_keyword(one_line):
                #pdb.set_trace()
                tag_name = one_line.strip(tag).rstrip('\n')
                tag_name = tag_name.split(':')[0]
                tag_start = line_counter+1
                list_to_update.append((tag_name, tag_start, 0))
        # easiest way to calculate section end is to look at start of next element
        #pdb.set_trace()
        for count, one_section in enumerate(list_to_update):
            try:
                tag_end = list_to_update[count+1][1] - 1
            except IndexError:
                list_to_update[count] = (list_to_update[count][0], list_to_update[count][1], line_counter+1)
            else:
                list_to_update[count] = (list_to_update[count][0], list_to_update[count][1], tag_end)

    def move_section(self, section_from, section_to):
        buffer_space = self.dict[section_to] + self.dict[section_from]
        self.dict[section_to] = buffer_space
        self.dict[section_from] = ''

    def print_section(self, section_name):
        for line in self.dict[section_name]:
            print(line)

    def print_whole_thing(self):
        for k, v in six.iteritems(self.dict):
            print(k)
            self.print_section(k)

    def __str__(self):
        print_string = ''
        for one_section in self.sections:
            print_string += ('Section {}, start: {}, end: {}\n'.format(one_section[0], one_section[1], one_section[2]))
        for one_subsection in self.subsections:
            print_string += ('Section {}, start: {}, end: {}\n'.format(one_subsection[0], one_subsection[1], one_subsection[2]))
        pdb.set_trace()
        return print_string

def run_flask():
    app.run(debug=True)

if __name__ == '__main__':
    #app.run(host= '0.0.0.0', debug=True)
    #sys.exit(1)
    pdb.set_trace()
    tklr = Tklr('/installers/tklr_0_2.txt')
    #tklr.find_major_sections()
    tklr.find_sections(tklr.sections, tag='========== ', ignore='e.of', regex=r'========== ')
    tklr.find_sections(tklr.subsections, tag='    ', ignore='==', regex=r'    \S')
    tklr.load_dict()
    '''
    def find_major_sections(self):
        self.find_sections(self, self.sections, tag='========== ', ignore='e.of')

    def find_minor_sections(self):
        self.find_sections(self, self.subsections, tag='    ', ignore='==')
    '''
    print(tklr)
