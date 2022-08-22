#!/bin/bash

while getopts b:de FLAG
do
    case ${FLAG} in
	b)
	    BANK=${OPTARG}
	    ;;
	d)
	    DRY=-dry
	    ;;
	e)
	    EMPTY=-empty
	    ;;
	*)
	    echo "fdftocsv [-b<bank#>] [-d] [-e] #-d for dry run, -e to empty existing csv"
	    exit
	    ;;
    esac
done

for BLOB in blob${BANK:=0}*.fdf; do
    fdf2csv ${DRY} ${EMPTY} ${BLOB} || break
done
