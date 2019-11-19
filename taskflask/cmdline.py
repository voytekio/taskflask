import pdb

import taskflask.tklr as tklrlib
import taskflask.api as api

def run_flask():
    api.app.run(debug=True)

if __name__ == '__main__':
    api.app.run(host= '0.0.0.0', debug=True)
    sys.exit(1)
    #pdb.set_trace()
    tklr = tklrlib.Tklr('/installers/tklr_0_2.txt')
    #tklr.find_major_sections()
    tklr.find_sections(tklr.sections, tag='========== ', ignore='e.of', regex=r'========== ')
    tklr.find_sections(tklr.subsections, tag='    ', ignore='==', regex=r'    \S')
    tklr.load_dict()
    tklr.print_section('M5')
    '''
    def find_major_sections(self):
        self.find_sections(self, self.sections, tag='========== ', ignore='e.of')

    def find_minor_sections(self):
        self.find_sections(self, self.subsections, tag='    ', ignore='==')
    '''
