#!/bin/bash

for BLOB in $HOME/Desktop/blobs/blob*.fdf; do
    fdf2csv $BLOB
done
