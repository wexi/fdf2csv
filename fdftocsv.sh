#!/bin/bash

while getopts b:dse FLAG
do
    case ${FLAG} in
	b)
	    BANK=${OPTARG}
	    ;;
	d)
	    DRY=-dry
	    ;;
	s)
	    SKIP=-skip
	    ;;
	e)
	    EMPTY=-empty
	    ;;
	*)
	    echo "fdftocsv [-b<bank#>] [-d] [-s] [-e] # -d dry run, -s ignore unexpected fields, -e empty existing csv"
	    exit
	    ;;
    esac
done

for BLOB in blob${BANK:=0}*.fdf; do
    fdf2csv ${DRY} ${SKIP} ${EMPTY} ${BLOB} || break
    unset EMPTY
done
