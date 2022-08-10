#!/bin/bash

BANK=$1

for BLOB in blob${BANK:=0}*.fdf; do
    fdf2csv ${BLOB} || break
done
