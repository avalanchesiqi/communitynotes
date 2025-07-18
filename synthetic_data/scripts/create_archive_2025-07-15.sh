#!/bin/bash

# copy files matching the pattern 2025-07-10_results/raw_output/*/*/run_0/* to temp_zip/raw_output/ 
# while preserving the directory structure starting from raw_output
# Resulting directory structure:
# temp_zip/
# └── raw_output/
#     ├── SymUserPol/10_SymUserPol/run_0/scored_notes.tsv
#     ├── iu_Variance/Var_Iu_01/run_0/aux_note_info.tsv
#     └── ... (other files)

# Create temp directory
mkdir -p temp_zip/raw_output

# Find and copy files, preserving structure from raw_output onwards
find 2025-07-10_results/raw_output -path "*/run_0/*" -type f -exec sh -c '
    # Extract the path starting from raw_output
    relative_path="${1#2025-07-10_results/}"
    dest="temp_zip/$relative_path"
    mkdir -p "$(dirname "$dest")"
    cp "$1" "$dest"
' _ {} \;

# Change to the raw_output directory
cd temp_zip/raw_output/

# Zip from here (this will exclude the parent directories)
zip -r ../../2025-07-10_results_raw.zip ./*

# Go back to original directory
cd ../../

zip 2025-07-10_results_figs.zip 2025-07-10_results/figs/* 2025-07-10_results/fp_raw_count/*
