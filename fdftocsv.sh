#!/bin/bash
# fdftocsv.sh — extract max column CSV from blob*.fdf files

# resolve symlink to get the real script path
SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
# now get its directory
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
FDF2CSV="$SCRIPT_DIR/fdf2csv.py"

set -euo pipefail      # exit on any error, undefined variable references are errors,
                       # and pipeline failures are caught
shopt -s nullglob      # allow globs to expand to an empty list if no matches

# Collect all FDF files matching the pattern blobNNNN.fdf
blobs=(blob*.fdf)

# Exit with error if no FDF files are found
if (( ${#blobs[@]} == 0 )); then
  echo "ERROR: no FDF record found" >&2
  exit 1
fi

# Try each file as the candidate header in numerical order
for HEAD in "${blobs[@]}"; do
  # Remove any existing CSV file to start fresh
  rm -f blob.csv

  # Attempt to build the CSV header from this file, suppressing output
  if $FDF2CSV -quiet "$HEAD" >/dev/null 2>&1; then
    # If header creation succeeds, test every other FDF against it
    for NEXT in "${blobs[@]}"; do
      # Skip the file used as the header source
      [[ "$NEXT" == "$HEAD" ]] && continue

      # Run $FDF2CSV; if it fails, this header is incomplete
      if ! $FDF2CSV -quiet "$NEXT" >/dev/null 2>&1; then
        # Clean up partial CSV and try next candidate as header
        rm -f blob.csv
        continue 2
      fi
    done

    # If all other files succeeded, keep blob.csv and exit
    exit 0
  fi
done

# If we reach here, no single FDF file covered all columns
echo "ERROR: no FDF record has all headers" >&2
exit 1
