from __future__ import print_function
from collections import OrderedDict
from datetime import datetime, timedelta
from dateutil import tz
from shutil import copyfile, copy
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
        self.dont_match_keywords = [
            'today',
            'DAILY',
            'URGENTs',
            'Awaits',
            'Misc',
            'NOTES',
            'EVENING',
            'BRAINDEAD',
            'DONEs',
        ]
        self.searchtags = {
            'major_sections': {
                'tag': '========== ',
                'ignore': 'e.of',
                'regex': r'========== '},
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
        ''' checks if line contains one of the keywords from the dont_match_keywords dict '''
        for keyword in self.dont_match_keywords:
            #print('kword: {}, line: {}'.format(keyword, line))
            if keyword in line:
                #print('SKIP')
                return True
        return False

    def read_file(self, filename):
        print('Using file: {}'.format(filename))
        with open(filename) as f:
            for one_line in f:
                self.file_contents.append(one_line.strip('\n'))

    def load_full_dict(self):
        ''' uses metadata from find_sections for both major and minor subsections and populates
            content of the self.dict dictionary with all subsections
        '''
        # compute major sections metadata
        #res = self.find_sections(self.sections, tag=self.searchtags['major_sections']['tag'], ignore=self.searchtags['major_sections']['ignore'], regex=self.searchtags['major_sections']['regex'])
        #pdb.set_trace()
        major = self.searchtags['major_sections']
        tag, ignore_string, regex = major['tag'], major['ignore'], major['regex']
        major_metadata = self.find_sections(tag, ignore_string, regex)
        self.sections = major_metadata
        print('Major sections: {}'.format(self.sections))
        # compute minor subsections metadata
        for section in self.sections:
            name = section[0]
            minor = self.searchtags[name]
            tag, ignore_string, regex = minor['tag'], minor['ignore'], minor['regex']
            #tag, ignore_string, regex = self.searchtags[name]
            minor_metadata = self.find_sections(tag, ignore_string, regex, start=section[1], end=section[2])
            major_mod = (section[0], section[1], (minor_metadata[0][1])-1, section[3]) 
            self.subsections.append(major_mod) # also insert major section as subsection so everything gets printed
            for one_tuple in minor_metadata:
                self.subsections.append(one_tuple)
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


    def find_sections(self, tag, ignore_string, regex, start=0, end=None):
        '''
        parse input - using magic tags, discover subsections and note their names,
        start and end locations.
        this only stores metadata about subsections into a list, load_dict func will 
        use this to retrieve data and store actual contents. 
        '''
        if not self.file_contents:
            self.read_file(self.filename)
        temp_list = []
        temp_list = self.file_contents[start:] if not end else self.file_contents[start:end]
        ret_list = []
        for line_counter, one_line in enumerate(temp_list):
            if re.match(regex, one_line) and ignore_string not in one_line and not self.match_keyword(one_line):
                #pdb.set_trace()
                tag_name = one_line.strip(tag).rstrip('\n')
                tag_name = tag_name.split(':')[0]
                section_full_name = one_line
                section_start = line_counter+1 + start
                ret_list.append((tag_name, section_start, 0, section_full_name))
        # easiest way to calculate section end is to look at start of next element
        for count, one_section in enumerate(ret_list):
            try:
                section_end = ret_list[count+1][1] - 1 # + start
            except IndexError:
                ret_list[count] = (ret_list[count][0], ret_list[count][1], line_counter+1 + start, ret_list[count][3])
            else:
                ret_list[count] = (ret_list[count][0], ret_list[count][1], section_end, ret_list[count][3])
        return ret_list

    def print_today(self):
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('America/New_York')
        today = datetime.now()
        today = today.replace(tzinfo=from_zone)
        today_local = today.astimezone(to_zone)
        return self.get_section(today_local.strftime('%d'))


    def move_today(self):
        #day = figure_day():
        # date shananigans
        from_zone = tz.gettz('UTC')
        to_zone = tz.gettz('America/New_York')
        # METHOD 2: Auto-detect zones:
        #from_zone = tz.tzutc()
        #to_zone = tz.tzlocal()
        #pdb.set_trace()
        today = datetime.now()
        yesterday = today - timedelta(hours=24)
        # Tell the datetime object that it's in UTC time zone since 
        # datetime objects are 'naive' by default
        today = today.replace(tzinfo=from_zone)
        yesterday = yesterday.replace(tzinfo=from_zone)
        #utc = utc.replace(tzinfo=from_zone)
        # Convert time zone
        today_local = today.astimezone(to_zone)
        yesterday_local = yesterday.astimezone(to_zone)

        print('Moving from {} to {}.'.format(yesterday_local.strftime('%d'), today_local.strftime('%d')))
        self.move_section(str(yesterday_local.strftime('%d')), str(today_local.strftime('%d')))
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
        '''
        ret = ''
        for line in self.dict[section_name]['contents']:
            ret += line + '\n'
        return ret
        '''


    @staticmethod
    def generate_unused_bak_file_name(filename):
        new_filename = '{}.bak'.format(filename)
        return new_filename

    @staticmethod
    def copy_file(src, dst):
        #pdb.set_trace()
        print('Copying file {} to {}'.format(src,dst))
        try:
            copy(src, dst)
        except:
            print('ERROR copying file {} to {}'.format(src, dst))
            return False
        return True

    def find_len(self):
        ''' finds line count of the self.dict structure '''
        count = 0
        #pdb.set_trace()
        for k, v in six.iteritems(self.dict):
            #print(self.get_section(k))
            count += len(self.get_section(k).split('\n')) - 1
        return count

    def save_file(self):
        #pdb.set_trace()
        new_len = self.find_len()
        print('orig line count: {}, new file line count: {}'.format(len(self.file_contents), new_len))
        if abs(len(self.file_contents) - new_len) > 1:
            print('old and new files seem different by line counts, not proceeding')
            return False

        bak_filename = self.generate_unused_bak_file_name(self.filename)
        print('saving file: {}'.format(self.filename))
        if self.copy_file(self.filename, bak_filename):
            with open(self.filename, 'w') as f:
                for k, v in six.iteritems(self.dict):
                    f.write(self.get_section(k))
                return True
        else:
            print('backup copy not made, so not saving anything')
            return False

    def __str__(self):
        print('!!! old - may need revisiting')
        print_string = ''
        for one_section in self.sections:
            print_string += ('Section {}, start: {}, end: {}\n'.format(one_section[0], one_section[1], one_section[2]))
        for one_subsection in self.subsections:
            print_string += ('Section {}, start: {}, end: {}\n'.format(one_subsection[0], one_subsection[1], one_subsection[2]))
        #pdb.set_trace()
        return print_string


