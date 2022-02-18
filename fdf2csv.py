#!/usr/bin/python3
"""
#title           :fdf2csv.py
#description     :Extract all data from FDF file to a CSV file
#author          :trockenasche
#usage           :python fdf2csv.py file.fdf

#hacker          :wexi
#testing         :Acrobat Reader FDF's only
"""

import bisect
import csv
import os
import re
import sys
from codecs import BOM_UTF16_BE


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

# Where the magic happened
pattern = re.compile(rb'<</T\(([^\)]*)\)(/V[\(/]([^\)>]+)\)?>>)?')
fdf_list = re.findall(pattern, fdf)


def oct(mat):
    return int(b'0o' + mat.group(1), base=8).to_bytes(1, 'big')


def utf(bs):
    try:
        if bs.startswith(BOM_UTF16_BE):
            return bs.decode('utf_16')
        elif re.search(rb'\\[0-3][0-7][0-7]', bs):
            return utf(re.sub(rb'\\([0-3][0-7][0-7])', oct, bs))
        else:
            return bs.decode(codec)
    except UnicodeDecodeError:
        return '???'


csv_names = []
csv_values = []
for token in fdf_list:
    key = utf(token[0])
    if key not in ('Submit', 'Reset'):
        loc = bisect.bisect(csv_names, key)
        csv_names.insert(loc, key)
        value = utf(token[2])
        csv_values.insert(loc, value)

# Set the output filename based on input file
csv_fname = re.sub(r'\d*\.fdf$', '.csv', fname)

mode = 'rt' if os.path.isfile(csv_fname) else 'xt'
print('Creating' if mode == 'xt' else 'Adding to',
      os.path.basename(csv_fname))

if mode == 'rt':
    with open(csv_fname, mode) as f:
        rd = csv.DictReader(f)
        row = next(rd)
        names = list(row.keys())  # no need to sort
        if names != csv_names:
            print("Error: Fields mismatch")
            sys.exit(1)
        mode = 'at'

with open(csv_fname, mode) as f:
    wr = csv.writer(f)
    if mode == 'xt':
        wr.writerow(csv_names)
    wr.writerow(csv_values)
sys.exit(0)
