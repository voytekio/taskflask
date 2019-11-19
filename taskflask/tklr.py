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


