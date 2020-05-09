#!/usr/bin/python
from __future__ import print_function
import argparse
import pdb

import taskflask.tklr as tklrlib
#import taskflask.api as api

def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f","--filename", help="name of tklr file", action = 'store', default = 'tklr_0_2.txt')
    parser.add_argument("-p","--printsection", help="print section by name, ie M6", action = 'store')
    parser.add_argument("-m","--movesection", help="move section's contents from one to another section, -m 'M6-M7'", action = 'store')
    #parser.add_argument("-m","--mode", help="mode-either import or export", required=True, action = 'store')
    parser.add_argument("-t","--today", help="move yesterdays section to today", action = 'store_true')
    parser.add_argument("-w","--html", help="export to html", action = 'store_true')
    parser.add_argument("-a","--dayfix", help="fix days", action = 'store_true')
    parser.add_argument("-d","--debug", help="run in debugger", action = 'store_true')
    parser.add_argument("-n","--nosave", help="dont save or backup any files", action = 'store_true')
    # action = 'store' is default (and can even be omitted)
    # action = 'store_true' or 'store_false' are for flags:
    #     if user specifes --execute, then args.execute will evaulate to True; otherwise False
    args = parser.parse_args()
    return args

def run_flask():
    api.app.run(debug=True)

def main():
    args = parseargs()
    #api.app.run(host= '0.0.0.0', debug=True)
    if args.debug:
        pdb.set_trace()
    tklr = tklrlib.Tklr(args.filename, args.nosave, args.debug)
    tklr.load_full_dict()
    if args.printsection:
        print(tklr.get_section(args.printsection),end="")
    if args.movesection:
        from_section = args.movesection.split('-')[0]
        to_section = args.movesection.split('-')[1]
        tklr.move_section(from_section, to_section)
        print('--------- after move ------')
        print(tklr.get_section(from_section))
        print(tklr.get_section(to_section))
    if args.today:
        tklr.move_today()
        print(tklr.print_today())
        tklr.save_file()
    if args.html:
        tklr.make_html()
        tklr.add_headings()

    #tklr.move_section('09', '10')
    #print(tklr.get_section('M9'),end="")
    #tklr.print_all()

if __name__ == '__main__':
    main()

