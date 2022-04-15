

# Thanks

To [trockenasche](https://github.com/trockenasche/fdf2csv) for starting this project. It seems that the original
author todo-s have been fully implemented, and perhaps some more.


# General

FDF is the original [PDF forms data (only) submission format](https://en.wikipedia.org/wiki/PDF#Forms). This script
converts such files to the popular CSV "spreadsheet" format. It should be
easy to execute this script on multiple identical format FDF files, to
build a large single CSV.


# Usage

fdf2csv.py filename[#\*.fdf]

Adds row/data to the outaput filename.csv if it exists. It is assumed that
the FDF fields are unique; They would become the CSV column names.

A \_serno field is introduced if the input filename has a trailing serial
number.

The input filename can include the file path (with a leading tilde for
home page). The output CSV has the trailing digits removed.

