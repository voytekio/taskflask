from __future__ import print_function
from collections import OrderedDict
from datetime import datetime, timedelta
from dateutil import tz
from shutil import copyfile, copy
import fileinput
import six
import re

import pdb

class Tklr():
    def __init__(self, filename, no_save):
        self.now = datetime.now()
        self.no_save = no_save
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
        #pdb.set_trace()
        major = self.searchtags['major_sections']
        tag, ignore_string, regex = major['tag'], major['ignore'], major['regex']
        self.sections = self.find_sections(tag, ignore_string, regex)
        print('Major sections: {}'.format(self.sections))

        # compute minor subsections metadata
        for section in self.sections:
            name = section[0]
            minor = self.searchtags[name]
            tag, ignore_string, regex = minor['tag'], minor['ignore'], minor['regex']
            #tag, ignore_string, regex = self.searchtags[name]
            minor_metadata = self.find_sections(tag, ignore_string, regex, start=section[1], end=section[2])
            major_mod = (section[0], section[1], (minor_metadata[0][1])-1, section[3]) 
            self.subsections.append(major_mod) # also insert major section as subsection
                # so everything gets included in subsection dir - both major and minor headings
            for one_tuple in minor_metadata:
                self.subsections.append(one_tuple)
        # store actual contents in dict
        for one_subsection in self.subsections:
            self.dict[one_subsection[0]] = {}
            self.dict[one_subsection[0]]['heading'] = one_subsection[3]
            self.dict[one_subsection[0]]['contents'] = self.file_contents[one_subsection[1]:one_subsection[2]]


    def find_sections(self, tag, ignore_string, regex, start=0, end=None):
        '''
        parse input - using magic tags, discover subsections and note their names,
        start and end locations.
        this only stores metadata about subsections into a list, load_dict func will 
        use this to retrieve data and store actual contents. 
        RETURN: list of tuples indicating section headers names, starts and ends:
            ex: [('INs', 1, 54, '========== INs'), ('projects', 55, 1402, '========== projects')]
        '''
        if not self.file_contents:
            self.read_file(self.filename)
        temp_list = []
        temp_list = self.file_contents[start:] if not end else self.file_contents[start:end]
        ret_list = []
        for line_counter, one_line in enumerate(temp_list):
            if re.match(regex, one_line) and ignore_string not in one_line and not self.match_keyword(one_line):
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


    def day_fix(self):
        '''
        inside calendar major section, for each day as int, fix the day name as string
        '''
        # iterate over dict, find only the day sections(regex using the definition?), ignore rest
        outside_calendar = False
        for sname, section_value in six.iteritems(self.dict):
            #print(sname)
            if re.match(r'\d\d', sname): # ex: match 01 but not M12 or travel
                try:
                    replaced_date = datetime.strptime('{}/{}/{}'.format(self.now.month, sname, self.now.year), '%m/%d/%Y')
                    rep2 = replaced_date.strftime('%a')
                except ValueError:
                    rep2 = 'N/A'
                new_name = '{0}{1}: ({2})'.format(self.searchtags['calendar']['tag'],
                    sname, rep2)
                section_value['heading'] = new_name

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

    def get_section(self, section_name, debug=True):
        if debug:
            minors = ''
            for k, v in six.iteritems(self.dict):
                minors = minors + k + ','
            print('Minor sections: ({})'.format(minors))
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
        if self.no_save:
            print('no save requested, will print to screen only')
            print(self.__str__())
            return

        # check line counts and back out if not equal
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
        print_string = ''
        for k, v in six.iteritems(self.dict):
            print_string += (self.get_section(k))
        return print_string

    @staticmethod
    def generate_html_filename(filename):
        #pdb.set_trace()
        new_filename = '{}.html'.format(filename)
        return new_filename


    @staticmethod
    def count_spaces(string):
        #pdb.set_trace()
        for counter,char in enumerate(string):
            if char != " ":
                return counter
        return 0

    def make_html(self):
        html_filename = self.generate_html_filename(self.filename)
        print('saving file: {}'.format(html_filename))
        #pdb.set_trace()
        with open(html_filename, 'w') as f:
            for oneline in self.file_contents:
                spaces = self.count_spaces(oneline)*"&nbsp"
                f.write("{}{}{}".format(spaces, oneline.lstrip() ,' <br>\n'))
                #for k, v in six.iteritems(self.dict):
                #    f.write(self.get_section(k))
            return True

    def add_headings(self):
        ''' finds section starts and replaces it with html h2 tag '''
        majors = []
        majors = self.sections
        html_filename = self.generate_html_filename(self.filename)
        html_header = '<html>\n<title>foo_title</title>\n<body>\n'
        html_footer = '</body></html>\n'

        counter2 = 0
        section_start = majors[counter2][1]
        section_name = majors[counter2][0]
        #pdb.set_trace()
        #for line in fileintpue.FileInput('foo.html'):
        for counter, line in enumerate(fileinput.FileInput(html_filename, inplace=1)):
            if counter == 0:
                print(html_header)
                print(self.add_html_toc())
            if counter+1 == section_start:
                print('<h2 id="{}">{}</h2>'.format(section_name, line))
                counter2 = counter2 + 1
                try:
                    section_start = majors[counter2][1]
                    section_name = majors[counter2][0]
                except IndexError:
                    pass
            else:
                print(line)
        with open(html_filename, 'a') as f:
            f.write(html_footer)

    def add_html_toc(self):
        ''' adds Table of Contents '''
        ret_string = '<h3>Contents</h3>\n<ol>\n'
        for one_major in self.sections:
            section_name = one_major[0]
            ret_string += '  <li><a href="#{0}">{0}</a></li>\n'.format(section_name)
        ret_string += '</ol>'
        return ret_string


