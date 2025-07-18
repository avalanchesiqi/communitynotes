#!/bin/bash
## This script will be called from the project root directory `communitynotes`
NOTES_FILE="${1:-}"
PARENT_OUTDIR="${2:-}"
START_IDX="${3:-0}" # default to 0
END_IDX="${4:-50}" # default to 50

mkdir -p "$PARENT_OUTDIR"

# get the prefix of the enrollment file
FILENAME=$(basename "$NOTES_FILE")
f_prefix=${FILENAME%-notes-00000.tsv}
# Other input files have the same prefix, but different suffixes, so we need to get the subdirectory name
# NOTES_FILE is typically in the form of synthetic_data/2025-07-03_polarize_data/U Polarize (sym)/*-notes-00000.tsv
SUBDIR=$(dirname "$NOTES_FILE")
ENROLLMENT="${SUBDIR}/${f_prefix}_userEnrollment-00000.tsv"
RATINGS="${SUBDIR}/${f_prefix}-ratings-00000.tsv"
# status is always the same
STATUS="sourcecode/data/tiny_data/tiny-noteStatusHistory-00000.tsv"

# echo "** run_multiple_times.sh NOTE_FILE: $NOTES_FILE"
# echo "prefix: $f_prefix"
# echo "PARENT_OUTDIR: $PARENT_OUTDIR"
# echo "SUBDIR: $SUBDIR"
# echo "ENROLLMENT: $ENROLLMENT"
# echo "RATINGS: $RATINGS"

# Enforce that START_IDX is less than or equal to END_IDX
if [ "$START_IDX" -gt "$END_IDX" ]; then
  echo "Error: Start index (second argument: $START_IDX) must be less than or equal to end index (third argument: $END_IDX)." >&2
  exit 1
fi

echo "Running from $START_IDX to $END_IDX"

# Create CSV file with headers
echo "input_file,output_file,start_time,end_time,duration" > "$PARENT_OUTDIR/timing_results_${START_IDX}.${END_IDX}.csv"


# Run the command 100 times
for i in $(seq $START_IDX $((END_IDX-1))); do
    # Create indexed output directory
    OUTPUT_DIR="$PARENT_OUTDIR/run_${i}"
    echo "Output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
    
    # Check if output files already exist
    if [ -f "$OUTPUT_DIR/scored_notes.tsv" ] && [ -f "$OUTPUT_DIR/helpfulness_scores.tsv" ]; then
        # echo "Output files already exist for run $i, skipping..."
        continue
    else
        echo "Output files do not exist for run $i, running sourcecode/main.py..."
    fi
    
    # Record start time
    start_time=$(date +%s.%N)
    
    # Run the command
    python sourcecode/main.py \
        --enrollment "$ENROLLMENT" \
        --notes "$NOTES_FILE" \
        --ratings "$RATINGS" \
        --status "$STATUS" \
        --outdir "$OUTPUT_DIR" \
        --noenforce-types \
        --nocheck-flips \
        --nopseudoraters \
        --nostrict-columns \
        --no-parquet \
        --scorers MFCoreScorer &> "$OUTPUT_DIR/main_tiny.log"
    
    # Record end time
    end_time=$(date +%s.%N)
    
    # Calculate duration
    duration=$(echo "$end_time - $start_time" | bc)
    
    # Append timing information to CSV
    echo "$ENROLLMENT,$OUTPUT_DIR,$start_time,$end_time,$duration" >> "$PARENT_OUTDIR/timing_results_${START_IDX}.${END_IDX}.csv"
    
    echo "Completed run $i"
done

echo "All runs completed. Timing results saved to $PARENT_OUTDIR/timing_results_${START_IDX}.${END_IDX}.csv"