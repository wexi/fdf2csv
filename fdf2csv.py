#!/usr/bin/python3
"""
#title           :fdf2csv.py
#description     :Extract all data from FDF file to a CSV file
#author          :trockenasche
#usage           :python fdf2csv.py file.fdf

#hacker          :wexi
#testing         :Acrobat Reader FDF's only

#Note            :First FDF file in a sequence sets the order of coloumns
                 :Rich text in the FDF is not discoverable
"""

import csv
import os
import re
import sys
from codecs import BOM_UTF16_BE
from collections import OrderedDict

arg = sys.argv[1:]
dry = arg and arg[0] == '-dry'
if dry:                         # only display number of columns
    arg.pop(0)

skip = arg and arg[0] == '-skip'
if skip:                        # ignore unknown columns
    arg.pop(0)

empty = arg and arg[0] == '-empty'
if empty:                       # rewrite csv file
    arg.pop(0)

if not arg or arg[0].startswith('-'):
    print("Usage: fdf2csv.py [-dry] [-skip] [-empty] file[.fdf] [codec]")
    sys.exit(1)


codec = 'latin1' if not arg[1:] else arg[1]
try:
    b'1234'.decode(codec)
except LookupError as e:
    print(e)
    sys.exit(1)

# check if the file exist
fname = os.path.expanduser(arg[0])
if fname.endswith('.'):
    fname += 'fdf'
elif not fname.endswith('.fdf'):
    fname += '.fdf'

try:
    with open(fname, 'rb') as f:
        fdf = f.read()
except FileNotFoundError as e:
    print(e)
    sys.exit(1)

if not fdf.startswith(b'%FDF-1.2'):
    print('Missing FDF signature')
    sys.exit(1)

# where magic happens
pattern = re.compile(rb'<</T\(([^\)]*)\)(/V([^>]*))?>>')
finds = re.findall(pattern, fdf)
fdf_list = [(find[0],
             find[2][1:] if find[2].startswith(b'/') else find[2][1:-1]
             if find[1] else b'') for find in finds]


def oct(mat):
    return int(b'0o' + mat.group(1), base=8).to_bytes(1, 'big')


def esc(mat):
    return mat.group(1)


def utf(bs):
    try:
        if bs.startswith(BOM_UTF16_BE):
            return bs.decode('utf_16')
        elif re.search(rb'\\[0-3][0-7][0-7]', bs):
            return utf(re.sub(rb'\\([0-3][0-7][0-7])', oct, bs))
        elif re.search(rb'\\[\(\)]', bs):
            return utf(re.sub(rb'\\([\(\)])', esc, bs))
        else:
            return bs.decode(codec)
    except UnicodeDecodeError:
        return '???'


csv_table = OrderedDict()

se = re.search(r'(\d+)\.fdf$', fname)
if se and se.group(1):
    csv_table['_serno'] = int(se.group(1))

for token in fdf_list:
    key = utf(token[0])
    if key not in ('Submit', 'Reset'):
        csv_table[key] = utf(token[1])

if dry:
    print(fname, '#fields:', len(csv_table))
    sys.exit(0)

csv_path = re.sub(r'\d*\.fdf$', '.csv', fname)
csv_file = os.path.basename(csv_path)
mode = 'xt' if not os.path.isfile(csv_path) else ('wt' if empty else 'at')

if mode != 'xt':
    with open(csv_path, 'rt') as f:
        rd = csv.reader(f)
        keys = next(rd)
        odds = set(csv_table.keys()) - set(keys)
        if odds:
            if not skip:
                print(fname, 'Unexpected column name(s):', odds)
                sys.exit(1)
            for odd in odds:
                csv_table.pop(odd)
        table = OrderedDict(zip(keys, ('',)*len(keys)))
        table.update(csv_table)

with open(csv_path, mode) as f:
    wr = csv.writer(f)
    if mode == 'at':
        wr.writerow(table.values())
        print(fname, 'add to', csv_file)
    else:
        if mode == 'xt':
            wr.writerow(csv_table.keys())
            wr.writerow(csv_table.values())
        else:
            wr.writerow(table.keys())
            wr.writerow(table.values())
        print(fname, 'create, add to', csv_file)
sys.exit(0)
