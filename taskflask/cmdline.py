from __future__ import print_function
import pdb

import taskflask.tklr as tklrlib
import taskflask.api as api

def run_flask():
    api.app.run(debug=True)

if __name__ == '__main__':
    #api.app.run(host= '0.0.0.0', debug=True)
    #sys.exit(1)
    #pdb.set_trace()
    #tklr = tklrlib.Tklr('/installers/tklr_0_2.txt')
    tklr = tklrlib.Tklr('/installers/tklr_0_2_test.txt')
    #tklr.find_major_sections()
    tklr.load_full_dict()
    #tklr.find_sections(tklr.sections, tag='========== ', ignore='e.of', regex=r'========== ')
    #tklr.find_sections(tklr.subsections, tag='    ', ignore='==', regex=r'    \S')
    #tklr.load_dict()
    #print(tklr.get_section('M5'),end="")
    #print(tklr.get_section('M6'),end="")
    pdb.set_trace()
    tklr.move_section('09', '10')
    #print(tklr.get_section('M5'),end="")
    #print(tklr.get_section('M6'),end="")
    tklr.print_all()
    '''
    def find_major_sections(self):
        self.find_sections(self, self.sections, tag='========== ', ignore='e.of')

    def find_minor_sections(self):
        self.find_sections(self, self.subsections, tag='    ', ignore='==')
    '''
