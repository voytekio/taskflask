from __future__ import print_function
from collections import OrderedDict
import six
import re

import pdb

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
        self.searchtags = {
            'INs': {
                'tag': '    ',
                'ignore': '==',
                'regex': r'    \S'},
            'projects': {
                'tag': '',
                'ignore': '=====',
                'regex': r'\S'},
            'calendar': {
                'tag': '    ',
                'ignore': '==',
                'regex': r'    \S'},
        }

    def match_keyword(self, line):
        for keyword in self.keywords:
            #print('kword: {}, line: {}'.format(keyword, line))
            if keyword in line:
                #print('SKIP')
                return True
        return False

    def read_file(self, filename):
        with open(filename) as f:
            for one_line in f:
                self.file_contents.append(one_line.strip('\n'))

    def load_full_dict(self):
        #pdb.set_trace()
        # compute major sections metadata
        self.find_sections(self.sections, tag='========== ', ignore='e.of', regex=r'========== ')
        # compute minor subsections metadata
        for section in self.sections:
            name = section[0]
            self.find_sections(self.subsections, tag=self.searchtags[name]['tag'], ignore=self.searchtags[name]['ignore'], regex=self.searchtags[name]['regex'], start=section[1], end=section[2])
        # store actual contents in dict
        for one_subsection in self.subsections:
            self.dict[one_subsection[0]] = {}
            self.dict[one_subsection[0]]['heading'] = one_subsection[3]
            self.dict[one_subsection[0]]['contents'] = self.file_contents[one_subsection[1]:one_subsection[2]]


    """
    def load_dict(self):
        '''
        go through all subsection markers and read file contents and put into a dict structure
        '''
        #pdb.set_trace()
        for one_subsection in self.subsections:
            self.dict[one_subsection[0]] = self.file_contents[one_subsection[1]:one_subsection[2]]
    """


    def find_sections(self, list_to_update, tag='========== ', ignore='e.of', regex=r'    \S', start=0, end=None):
        '''
        using magic tags, discover subsections and note their names, start and end locations
        this only stores metadata about subsections into a list, load_dict func will 
        use this to retrieve data and store actual contents. 
        '''
        #pdb.set_trace()
        if not self.file_contents:
            self.read_file(self.filename)
        temp_list = []
        temp_list = self.file_contents[start:] if not end else self.file_contents[start:end]
        #for line_counter, one_line in enumerate(self.file_contents):
        for line_counter, one_line in enumerate(temp_list):
            if re.match(regex, one_line) and ignore not in one_line and not self.match_keyword(one_line):
                #pdb.set_trace()
                tag_name = one_line.strip(tag).rstrip('\n')
                tag_name = tag_name.split(':')[0]
                section_full_name = one_line
                section_start = line_counter+1 + start
                list_to_update.append((tag_name, section_start, 0, section_full_name))
        # easiest way to calculate section end is to look at start of next element
        #pdb.set_trace()
        for count, one_section in enumerate(list_to_update):
            try:
                section_end = list_to_update[count+1][1] - 1 # + start
            except IndexError:
                #pdb.set_trace()
                list_to_update[count] = (list_to_update[count][0], list_to_update[count][1], line_counter+1 + start, list_to_update[count][3])
            else:
                list_to_update[count] = (list_to_update[count][0], list_to_update[count][1], section_end, list_to_update[count][3])

    def move_tdy(self):
        #day = figure_day():
        #move_section(day, day+1)
        return 0

    def move_section(self, section_from, section_to):
        '''
        takes contents of one section and appends/prepends to another
        does not move headings, only contents
        '''
        buffer_space = self.dict[section_to]['contents'] + self.dict[section_from]['contents']
        self.dict[section_to]['contents'] = buffer_space
        self.dict[section_from]['contents'] = ''

    def get_section(self, section_name):
        ret = ''
        #pdb.set_trace()
        ret = self.dict[section_name]['heading'] + '\n'
        for line in self.dict[section_name]['contents']:
            ret += line + '\n'
        return ret

    def print_section(self, section_name):
        return 'dont use, use get_section instead'
        ret = ''
        for line in self.dict[section_name]['contents']:
            ret += line + '\n'
        return ret

    def print_all(self):
        new_filename = '{}-1'.format(self.filename)
        with open(new_filename, 'w') as f:
            for k, v in six.iteritems(self.dict): #print(k)
                #pdb.set_trace()
                #print(v['heading'])
                #f.write(v['heading']+'\n')
                print(self.get_section(k), end="")
                f.write(self.get_section(k))

    def __str__(self):
        print('!!! old - may need revisiting')
        print_string = ''
        for one_section in self.sections:
            print_string += ('Section {}, start: {}, end: {}\n'.format(one_section[0], one_section[1], one_section[2]))
        for one_subsection in self.subsections:
            print_string += ('Section {}, start: {}, end: {}\n'.format(one_subsection[0], one_subsection[1], one_subsection[2]))
        #pdb.set_trace()
        return print_string


