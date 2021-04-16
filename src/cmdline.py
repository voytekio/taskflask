#!/usr/bin/python
'''
cmdline interface to tklr tool
'''
from __future__ import print_function, absolute_import
import argparse
import pdb

import taskflask.tklr as tklrlib
#import taskflask.api as api

def parseargs():
    ''' parse arguments '''
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--filename",
        help="name of tklr file",
        action='store',
        default='tklr_0_2.txt'
        )
    parser.add_argument("-p", "--printsection", help="print section by name, ie M6", action='store')
    parser.add_argument(
        "-z",
        "--desiredtimezone",
        help="specify different timezone than local machine. See https://en.wikipedia.org/wiki/List_of_tz_database_time_zones. Example: -z 'Europe/Warsaw'",  # pylint: disable=line-too-long
        action='store',
    )

    parser.add_argument("-r", "--printtoday", help="print today's section", action='store_true')
    parser.add_argument(
        "-m",
        "--movesection",
        help="move section's contents from one to another section, -m 'M6-M7'",
        action='store'
        )
    parser.add_argument(
        "-t",
        "--today",
        help="move yesterdays section to today",
        action='store_true'
        )
    parser.add_argument("-w", "--html", help="export to html", action='store_true')
    parser.add_argument("-a", "--dayfix", help="fix days", action='store_true')
    parser.add_argument("-d", "--debug", help="run in debugger", action='store_true')
    parser.add_argument("-n", "--nosave", help="dont save or backup any files", action='store_true')
    parser.add_argument(
        "-c",
        "--daycount",
        help="use with -t, how many days to go back to",
        action='store',
        default='1'
        )
    args = parser.parse_args()
    return args

# def run_flask():
#    api.app.run(debug=True)

def main():  # pylint: disable=missing-docstring
    args = parseargs()
    #api.app.run(host= '0.0.0.0', debug=True)
    if args.debug:
        pdb.set_trace()
    tklr = tklrlib.Tklr(args.filename, args.nosave, args.debug, args.desiredtimezone)
    tklr.load_full_dict()
    if args.printsection:
        print(tklr.get_section(args.printsection), end="")
    if args.printtoday:
        print(tklr.print_today())
    if args.movesection:
        from_section = args.movesection.split('-')[0]
        to_section = args.movesection.split('-')[1]
        tklr.move_section(from_section, to_section)
        print('--------- after move ------')
        print(tklr.get_section(from_section))
        print(tklr.get_section(to_section))
    if args.today:
        tklr.move_today(int(args.daycount))
        print(tklr.print_today())
        tklr.save_file()
    if args.dayfix:
        tklr.day_fix()
        tklr.save_file()
    if args.html:
        tklr.make_html()
        tklr.add_headings()

    #tklr.move_section('09', '10')
    #print(tklr.get_section('M9'),end="")
    #tklr.print_all()

if __name__ == '__main__':
    main()
