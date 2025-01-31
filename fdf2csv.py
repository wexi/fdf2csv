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
from csv import Dialect
from codecs import BOM_UTF16_BE, lookup
from collections import OrderedDict

arg = sys.argv[1:]
Dry = arg and arg[0] == '-dry'
if Dry:                         # only display number of columns
    arg.pop(0)

Tab = arg and arg[0] == '-tab'
if Tab:                         # excel or excel_tab CSV format
    arg.pop(0)
    
Skip = arg and arg[0] == '-skip'
if Skip:                        # ignore unknown columns
    arg.pop(0)

Empty = arg and arg[0] == '-empty'
if Empty:                       # rewrite csv file
    arg.pop(0)

Quiet = arg and arg[0] == '-quiet'
if Quiet:
    arg.pop(0)
    
if not arg or arg[0].startswith('-'):
    print("Usage: fdf2csv.py [-dry] [-tab] [-skip] [-empty] [-quiet] file[.fdf] [codec]", file=sys.stderr)
    sys.exit(1)

fname = os.path.expanduser(arg[0])
if fname.endswith('.'):
    fname += 'fdf'

try:
    with open(fname, 'rb') as f:
        fdf = f.read()
        assert fdf.startswith(b'%FDF-1.2')
        arg.pop(0)
        se = re.search(rb'/Encoding\s*/([a-zA-Z0-9_-]+)\b', fdf)
        codec = se[1].decode() if se else arg[0] if arg else 'latin1'
        lookup(codec)
        if not fname.endswith('.fdf'):
            fname += '.fdf'
except FileNotFoundError as e:
    print(e, file=sys.stderr)
    sys.exit(1)
except AssertionError as e:
    print(e, file=sys.stderr)
    sys.exit(1)
except LookupError as e:
    print(e, file=sys.stderr)
    sys.exit(1)

pattern = re.compile(rb'<<\s*'
                     rb'/T\s*\(([^()]+)\)\s*'  # field name
                     rb'/V\s*(?:(?:\[?\(((?:(?!>>).)*)\)\]?)|(?:/([\w-]+)))\s*'  # value
                     rb'(?:/\w+\s+\d+\s*)*'  # flags
                     rb'>>')
finds = re.findall(pattern, fdf)
fdf_list = [(find[0], find[1] if find[1] else find[2]) for find in finds]


def oct(mat):
    return int(b'0o' + mat.group(1), base=8).to_bytes(1, 'big')


def esc(mat):
    return mat.group(1)


def utf(bs):
    try:
        if bs.startswith(BOM_UTF16_BE):
            return bs.decode('utf-16')
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
    if key.lower() not in ('submit', 'reset'):
        csv_table[key] = utf(token[1])

if Dry:
    print(fname, '#fields:', len(csv_table))
    sys.exit(0)

csv_path = re.sub(r'\d*\.fdf$', '.csv', fname)
csv_file = os.path.basename(csv_path)
mode = 'xt' if not os.path.isfile(csv_path) else ('wt' if Empty else 'at')

dialect = None
tab = '\t' if Tab else ','
if mode != 'xt':
    with open(csv_path, 'rt') as f:
        dialect = csv.Sniffer().sniff(f.read(1024))
        if dialect.delimiter != tab:
            print(fname, 'Unexpected CSV delimiter', file=sys.stderr)
            sys.exit(1)
        if dialect.escapechar is None:
            dialect.escapechar = '\\'
        f.seek(0)
        rd = csv.reader(f, dialect)
        keys = next(rd)
        odds = set(csv_table.keys()) - set(keys)
        if odds:
            if not Skip:
                print(fname, 'Unexpected column name(s):', odds, file=sys.stderr)
                sys.exit(1)
            for odd in odds:
                csv_table.pop(odd)
        table = OrderedDict(zip(keys, ('',)*len(keys)))
        table.update(csv_table)

with open(csv_path, mode) as f:
    if dialect is None:
        dialect = csv.excel_tab if Tab else csv.excel
    wr = csv.writer(f, dialect)
    if mode == 'at':
        wr.writerow(table.values())
        if not Quiet:
            print(fname, 'add to', csv_file)
    else:
        if mode == 'xt':
            wr.writerow(csv_table.keys())
            wr.writerow(csv_table.values())
        else:
            wr.writerow(table.keys())
            wr.writerow(table.values())
        if not Quiet:
            print(fname, 'create', csv_file)
sys.exit(0)
