''' tklr module '''
from __future__ import print_function, absolute_import
from collections import OrderedDict, namedtuple
from datetime import datetime, timedelta
import fileinput
import pdb  # pylint: disable=unused-import
import re
from shutil import copy

from dateutil import tz
import six


Section_Tuple_Class = namedtuple('Section_Tuple', 'name, start, end, full_name')  # pylint: disable=invalid-name

class Tklr(object):  # pylint:disable=too-many-instance-attributes
    '''
    main class for tklr project
    will contain the contents
    as well as metadata about sections
    also config data for sections (as of now)
    '''
    def __init__(self, filename, no_save, debug=False, desired_tz=None):
        self.now = datetime.now()
        self.desired_tz = desired_tz
        self.no_save = no_save
        self.sections = []
        self.subsections = []
        self.debug = debug
        self.filename = filename
        self.file_contents = []
        if not self.file_contents:
            self.read_file(self.filename)
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
        self.task_tags = {
            'tag': '        ',
            'ignore': '==',
            'regex': r'        \S'}

    def match_keyword(self, line):
        ''' checks if line contains one of the keywords from the dont_match_keywords dict '''
        for keyword in self.dont_match_keywords:
            #print('kword: {}, line: {}'.format(keyword, line))
            if keyword in line:
                #print('SKIP')
                return True
        return False

    def read_file(self, filename):
        ''' takes a filename, and reads it into self.file_contents var '''
        print('Using file: {}'.format(filename))
        with open(filename) as file_object:
            for one_line in file_object:
                self.file_contents.append(one_line.strip('\n'))

    def load_full_dict(self):
        ''' uses metadata from find_sections for both major and minor subsections and populates
            content of the self.dict dictionary with all subsections
            INTPUT: None? but uses self.searchtags to divide into sections and then subsections
            OUTPUT: None? but output artifact is full dict
        '''
        # compute major sections metadata
        # pdb.set_trace()
        major = self.searchtags['major_sections']
        tag, ignore_string, regex = major['tag'], major['ignore'], major['regex']
        self.sections = self.find_sections(tag, ignore_string, regex)
        print('Major sections: {}'.format(self.sections))

        # compute minor subsections metadata
        for section in self.sections:
            #pdb.set_trace()
            name = section.name
            minor = self.searchtags[name]
            tag, ignore_string, regex = minor['tag'], minor['ignore'], minor['regex']
            minor_metadata_list = self.find_sections(
                tag,
                ignore_string,
                regex,
                start=section.start,
                end=section.end
            )

            # also insert major section (header only) as subsection
            # so everything gets included in subsection list - both major and minor headings
            # otherwise, we will not print major headers
            major_header = Section_Tuple_Class(
                section.name,
                section.start,
                (minor_metadata_list[0].start)-1, section.full_name)
            self.subsections.append(major_header)

            for one_tuple in minor_metadata_list:
                self.subsections.append(one_tuple)
        # print all subsections now:
        #for section in self.subsections:
        #    print(section)

        self.load_into_dict()

    def load_into_dict(self):
        '''
        split the actual contents of the file by subsections and store in dict
        INPUT: None, works mostly with the self.subsections list
        OUTPUT: None, populates the self.dict structure
        '''
        #pdb.set_trace()
        for one_subsection in self.subsections:
            self.dict[one_subsection.name] = {}
            self.dict[one_subsection.name]['heading'] = one_subsection.full_name
            self.dict[one_subsection.name]['contents'] = self.file_contents[
                one_subsection.start : one_subsection.end
            ]

    def print2(self, input_list, meta_list):
        ''' print today's tasks '''
        #TODO: see if previous print funcs can to this
        for meta in meta_list:
            print('NAME: {}'.format(meta.name))
            for line in input_list['contents'][(meta.start - 1) : meta.end]:
                print(line)
            print('')

    def print_stats(self):
        ''' get # of items in today and print it'''
        today = datetime.now()
        today_adjusted = self.adjust_tz(today)
        today_tag = today_adjusted.strftime('%d')
        todays_section = self.dict.get(today_tag).get('contents')
        todays_tasks = self.find_sections2(todays_section, self.task_tags['tag'], self.task_tags['ignore'], self.task_tags['regex'])
        print('FOUND {} items in today'.format(len(todays_tasks)))

    def find_sections2(self, input_list, tag, ignore_string, regex, start=0, end=None):  # pylint:disable=too-many-arguments
        '''
        SUMMARY: same as find_section but use named_input rather than take from file
        '''
        temp_list = []
        temp_list = input_list[start:end]
        ret_list = []
        for line_counter, one_line in enumerate(temp_list):
            if (
                    re.match(regex, one_line)
                    and ignore_string not in one_line
                    and not self.match_keyword(one_line) #TODO: fix this - match_keywords and ignore_string seem the same
            ):
                tag_name = one_line.strip(tag).rstrip('\n')
                tag_name = tag_name.split(':')[0] if ':' in tag_name else tag_name
                section = Section_Tuple_Class(
                    name=tag_name,
                    start=line_counter+1+start,
                    end=0,
                    full_name=one_line
                )
                ret_list.append(section)
        # easiest way to calculate section end is to look at start of next element
        #pdb.set_trace()# if self.debug else None
        for count, one_section in enumerate(ret_list):
            try:
                section_end = ret_list[count+1].start - 1 #one line before start of next section
            except IndexError:
                ret_list[count] = Section_Tuple_Class(
                    name=one_section.name,
                    start=one_section.start,
                    end=line_counter+1 + start,  # pylint: disable=undefined-loop-variable
                    full_name=one_section.full_name
                )
            else:
                ret_list[count] = Section_Tuple_Class(
                    name=one_section.name,
                    start=one_section.start,
                    end=section_end,
                    full_name=one_section.full_name
                )
        return ret_list


    def find_sections(self, tag, ignore_string, regex, start=0, end=None):  # pylint:disable=too-many-arguments
        '''
        SUMMARY: parse input - using magic tags, discover subsections and note their names,
            start and end locations. This only stores metadata about subsections into a
            list, load_dict func will use this to retrieve data and store actual contents.
        INPUT: tag ('========== '), ignore_string ('e.of'), regex ('========== ')
            - not sure if tag and regex are both needed, maybe only regex
            - same for ignore_string since the func seems to call match_keyword
        RETURN: list of tuples indicating section headers names, starts and ends:
            ex: [('INs', 1, 54, '========== INs'), ('projects', 55, 1402, '========== projects')]
        '''
        temp_list = []
        temp_list = self.file_contents[start:] if not end else self.file_contents[start:end]
        ret_list = []
        for line_counter, one_line in enumerate(temp_list):
            if (
                    re.match(regex, one_line)
                    and ignore_string not in one_line
                    and not self.match_keyword(one_line)
            ):
                # pdb.set_trace()
                tag_name = one_line.strip(tag).rstrip('\n')
                tag_name = tag_name.split(':')[0]
                section = Section_Tuple_Class(
                    name=tag_name,
                    start=line_counter+1+start,
                    end=0,
                    full_name=one_line
                )
                ret_list.append(section)
        # easiest way to calculate section end is to look at start of next element
        #pdb.set_trace()# if self.debug else None
        for count, one_section in enumerate(ret_list):
            try:
                section_end = ret_list[count+1].start - 1 #one line before start of next section
            except IndexError:
                ret_list[count] = Section_Tuple_Class(
                    name=one_section.name,
                    start=one_section.start,
                    end=line_counter+1 + start,  # pylint: disable=undefined-loop-variable
                    full_name=one_section.full_name
                )
            else:
                ret_list[count] = Section_Tuple_Class(
                    name=one_section.name,
                    start=one_section.start,
                    end=section_end,
                    full_name=one_section.full_name
                )
        return ret_list


    def day_fix(self):
        '''
        inside calendar major section, for each day as int, fix the day name as string
        '''
        # iterate over dict, find only the day sections(regex using the definition?), ignore rest
        for sname, section_value in six.iteritems(self.dict):
            #print(sname)
            if re.match(r'\d\d', sname): # ex: match 01 but not M12 or travel
                try:
                    replaced_date = datetime.strptime(
                        '{}/{}/{}'.format(self.now.month, sname, self.now.year),
                        '%m/%d/%Y'
                    )
                    rep2 = replaced_date.strftime('%a')
                except ValueError:
                    rep2 = 'N/A'
                new_name = '{0}{1}: ({2})'.format(
                    self.searchtags['calendar']['tag'], sname, rep2
                )
                section_value['heading'] = new_name

    def adjust_tz(self, dateobj):
        ''' gets a date obj and desired timezone and
        1. injects local(os) timezone and
        2. adjusts date to desired timezone if diff from local
        '''
        # zone defs are here: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

        # Since datetime objects are 'naive' by default,
        # inject the timezone(local for now) data into them:
        os_tzone = tz.tzlocal()
        dateobj = dateobj.replace(tzinfo=os_tzone)  #11 6:05 PM EST

        # now get desired tz and convert it:
        print('Desired timezone is: {}'.format(self.desired_tz))
        desired_tz = tz.gettz(name=self.desired_tz) # if name is Falsy, it gets local timezone
        if not desired_tz:
            raise ValueError(
                "Unable to get timezone from string representation {}".format(
                    self.desired_tz
                )
            )

        # adjust to desired tz (if local it should do nothing)
        dateobj_in_desired_tz = dateobj.astimezone(desired_tz) #12 0:05 AM CES

        print('date_in_desired_tz: {}'.format(dateobj_in_desired_tz))
        return dateobj_in_desired_tz

    def print_today(self):
        ''' print_today '''
        today = datetime.now()
        today_adjusted = self.adjust_tz(today)
        return self.get_section(today_adjusted.strftime('%d'))


    def move_today(self, day_count):
        ''' goes back day_count days and
        moves their section contents to todays section
        '''
        today = datetime.now() #ex 11th 6:05 PM laptop time
        today_adjusted = self.adjust_tz(today) #12 0:05 AM

        for day_to_go_back_to in range(day_count, 0, -1):
            day_from = today_adjusted - timedelta(hours=24*day_to_go_back_to)  #11 0:05 AM
            print('day_from: {}'.format(day_from))
            day_to = day_from + timedelta(hours=24)                   #12 0:05 AM
            print('day_to: {}'.format(day_to))

            print(
                'Moving from {} to {}.'.format(
                    day_from.strftime('%d'),
                    day_to.strftime('%d')
                )
            )
            self.move_section(str(day_from.strftime('%d')), str(day_to.strftime('%d')))
        return 0

    def move_section(self, section_from, section_to):
        '''
        takes contents of one section and appends/prepends to another
        does not move headings, only contents
        '''
        buffer_space = self.dict[section_to]['contents'] + self.dict[section_from]['contents']
        self.dict[section_to]['contents'] = buffer_space
        self.dict[section_from]['contents'] = ''

    def get_section(self, section_name, debug=False):
        ''' retrieves one section and returns it to caller '''
        if debug:
            minors = ''
            for k, _ in six.iteritems(self.dict):
                minors = minors + k + ','
            print('Minor sections: ({})'.format(minors))
        ret = ''
        #pdb.set_trace()
        ret = self.dict[section_name]['heading'] + '\n'
        for line in self.dict[section_name]['contents']:
            ret += line + '\n'
        return ret

    @staticmethod
    def generate_unused_bak_file_name(filename):
        ''' generate_unused_bak_file_name '''
        new_filename = '{}.bak'.format(filename)
        return new_filename

    @staticmethod
    def copy_file(src, dst):
        ''' copy_file '''
        #pdb.set_trace()
        print('Copying file {} to {}'.format(src, dst))
        try:
            copy(src, dst)
        except BaseException:
            print('ERROR copying file {} to {}'.format(src, dst))
            return False
        return True

    def find_len(self):
        ''' finds line count of the self.dict structure '''
        count = 0
        #pdb.set_trace()
        for k, _ in six.iteritems(self.dict):
            #print(self.get_section(k))
            count += len(self.get_section(k).split('\n')) - 1
        return count

    def save_file(self):
        '''
        prints to screen,
        does safety checks like comparing line counts
        backs up a copy,
        then modifies the current file
        '''

        if self.no_save:
            print('no save requested, will print to screen only')
            print(self.__str__())
            return True

        # check line counts and back out if not equal
        new_len = self.find_len()
        print(
            'orig line count: {}, new file line count: {}'.format(
                len(self.file_contents), new_len
            )
        )
        if abs(len(self.file_contents) - new_len) > 1:
            print('old and new files seem different by line counts, not proceeding')
            return False

        bak_filename = self.generate_unused_bak_file_name(self.filename)
        print('saving file: {}'.format(self.filename))
        if self.copy_file(self.filename, bak_filename):
            with open(self.filename, 'w') as file_object:
                for k, _ in six.iteritems(self.dict):
                    file_object.write(self.get_section(k))
                return True
        else:
            print('backup copy not made, so not saving anything')
            return False

    def __str__(self):
        print_string = ''
        return 'skipping print to screen'
        for k, _ in six.iteritems(self.dict):
            print_string += (self.get_section(k))
        return print_string

    @staticmethod
    def generate_html_filename(filename):
        ''' generate name '''
        #pdb.set_trace()
        new_filename = '{}.html'.format(filename)
        return new_filename


    @staticmethod
    def count_spaces(string):
        ''' count leading spaces '''
        #pdb.set_trace()
        for counter, char in enumerate(string):
            if char != " ":
                return counter
        return 0

    def make_html(self):
        ''' creates html file from the main dict '''
        html_filename = self.generate_html_filename(self.filename)
        print('saving file: {}'.format(html_filename))
        #pdb.set_trace()
        with open(html_filename, 'w') as file_object:
            for oneline in self.file_contents:
                spaces = self.count_spaces(oneline)*"&nbsp"
                file_object.write("{}{}{}".format(spaces, oneline.lstrip(), ' <br>\n'))
                #for k, _ in six.iteritems(self.dict):
                #    file_object.write(self.get_section(k))
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
        with open(html_filename, 'a') as file_object:
            file_object.write(html_footer)

    def add_html_toc(self):
        ''' adds Table of Contents '''
        ret_string = '<h3>Contents</h3>\n<ol>\n'
        for one_major in self.sections:
            section_name = one_major[0]
            ret_string += '  <li><a href="#{0}">{0}</a></li>\n'.format(section_name)
        ret_string += '</ol>'
        return ret_string
