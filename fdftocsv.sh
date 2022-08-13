#!/bin/bash

while getopts b:d FLAG
do
    case ${FLAG} in
	b)
	    BANK=${OPTARG}
	    ;;
	d)
	    DRY=-dry
	    ;;
	*)
	    echo "fdftocsv [-b<bank#>] [-d] #-d for dry run"
	    exit
	    ;;
    esac
done

for BLOB in blob${BANK:=0}*.fdf; do
    fdf2csv ${DRY} ${BLOB} || break
done
