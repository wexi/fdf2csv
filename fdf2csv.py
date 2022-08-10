#!/usr/bin/python3
"""
#title           :fdf2csv.py
#description     :Extract all data from FDF file to a CSV file
#author          :trockenasche
#usage           :python fdf2csv.py file.fdf

#hacker          :wexi
#testing         :Acrobat Reader FDF's only

#Note            :First FDF file in a sequence should have all fields present
                 :Rich text in the FDF is not discoverable
"""

import csv
import os
import re
import sys
from codecs import BOM_UTF16_BE
from collections import OrderedDict

arglen = len(sys.argv)
if not 2 <= arglen <= 3:
    print("Usage: fdf2csv.py file[.fdf] [codec]")
    sys.exit(1)
codec = 'latin1' if arglen < 3 else sys.argv[2]
try:
    b'1234'.decode(codec)
except LookupError as e:
    print("Error: " + e.args[-1])
    sys.exit(1)

# check if the file exist
fname = os.path.expanduser(sys.argv[1])
if fname.endswith('.'):
    fname += 'fdf'
elif not fname.endswith('.fdf'):
    fname += '.fdf'
if not os.path.isfile(fname):
    print("Error: " + fname + " doesn't exist")
    sys.exit(1)

# open file
with open(fname, 'rb') as f:
    fdf = f.read()

if not fdf.startswith(b'%FDF-1.2'):
    print("Error: Missing FDF signature")
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


# Set the output filename based on input file
csv_fname = re.sub(r'\d*\.fdf$', '.csv', fname)

csv_table = OrderedDict()

se = re.search(r'(\d+)\.fdf$', fname)
if se and se.group(1):
    csv_table['_serno'] = int(se.group(1))

for token in fdf_list:
    key = utf(token[0])
    if key not in ('Submit', 'Reset'):
        csv_table[key] = utf(token[1])

xlsx = os.path.basename(csv_fname)
mode = 'rt' if os.path.isfile(csv_fname) else 'xt'

if mode == 'rt':
    with open(csv_fname, mode) as f:
        mode = 'at'
        rd = csv.reader(f)
        keys = next(rd)
        table = OrderedDict(zip(keys, ('',)*len(keys)))
        table.update(csv_table)
        if len(keys) < len(table):
            print(fname, 'mismatch with', xlsx)
            sys.exit(1)

with open(csv_fname, mode) as f:
    wr = csv.writer(f)
    if mode == 'xt':
        wr.writerow(csv_table.keys())
        wr.writerow(csv_table.values())
        print(fname, 'create and add to', xlsx)
    else:
        wr.writerow(table.values())
        print(fname, 'add to', xlsx)
sys.exit(0)
