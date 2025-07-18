#!/bin/bash
#####  Constructed by HPC everywhere #####
#SBATCH -A r00977
#SBATCH --mail-user=baotruon@iu.edu
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=50
#SBATCH --time=1-20:59:00
#SBATCH --mem=200gb
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --job-name=cn_test
#SBATCH --output=/N/project/community_notes_manip/communitynotes/synthetic_data/2025-07-10_results/running_logs/slurm_%j.out
#SBATCH --error=/N/project/community_notes_manip/communitynotes/synthetic_data/2025-07-10_results/running_logs/slurm_%j.err

## This script runs run_multiple_times.sh for each *notes.tsv file in the 2025-07-10_data subdirectories.
### RUN FROM PROJECT ROOT WITH: sbatch synthetic_data/2025-07-10_results/sbatch_by_file.sh
######  Job commands go below this line #####
cd /N/project/community_notes_manip/communitynotes

# Activate the Python environment
source /N/project/community_notes_manip/communitynotes/.venv/bin/activate

echo '###### Starting community notes test ######'
echo "Job started at $(date)"
echo "Running on node: $(hostname)"

# Function to monitor memory usage of a process
monitor_memory() {
    local pid=$1
    local log_file=$2
    local process_name=$3
    
    # Create CSV header
    echo "timestamp,process_name,pid,vm_size_mb,vm_rss_mb" > "$log_file"
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Starting memory monitoring for $process_name (PID: $pid)" >> "${log_file%.csv}.log"
    
    # Monitor memory usage every 5 minutes (300 seconds)
    while kill -0 "$pid" 2>/dev/null; do
        if [ -f "/proc/$pid/status" ]; then
            # Get memory info from /proc and convert KB to MB
            local vm_size_kb=$(grep "VmSize:" "/proc/$pid/status" | awk '{print $2}')
            local vm_rss_kb=$(grep "VmRSS:" "/proc/$pid/status" | awk '{print $2}')
            
            # Convert KB to MB (divide by 1024)
            local vm_size_mb=$(echo "scale=2; $vm_size_kb / 1024" | bc -l)
            local vm_rss_mb=$(echo "scale=2; $vm_rss_kb / 1024" | bc -l)
            
            local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
            echo "$timestamp,$process_name,$pid,$vm_size_mb,$vm_rss_mb" >> "$log_file"
        fi
        sleep 300
    done
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Memory monitoring ended for $process_name (PID: $pid)" >> "${log_file%.csv}.log"
}

# Create memory log directory
MEMORY_LOG_DIR="/N/project/community_notes_manip/communitynotes/synthetic_data/2025-07-10_results/running_logs/memory_logs_by_file"
mkdir -p "$MEMORY_LOG_DIR"

# Get the list of notes files (use the absolute path so that the .py script can be run from any directory)
NOTES_FILES=$(find /N/project/community_notes_manip/communitynotes/synthetic_data/2025-07-10_data -type f -name "*notes*.tsv")

# Convert to array for proper handling
NOTES_FILES_ARRAY=($NOTES_FILES)

# Check if any files were found
if [ ${#NOTES_FILES_ARRAY[@]} -eq 0 ]; then
    echo "ERROR: No notes files found in /N/project/community_notes_manip/communitynotes/synthetic_data/2025-07-10_data"
    exit 1
fi

# Number of parallel jobs
NO_PARALLELS=8

# Number of runs per file
NO_RUNS_PER_FILE=50

# Number of files
NO_FILES=${#NOTES_FILES_ARRAY[@]}
echo "### Total number of files: $NO_FILES ###"

# Calculate runs per parallel (ensure we get all 50 runs)
NO_RUNS_PER_PARALLEL=$(( (NO_RUNS_PER_FILE + NO_PARALLELS - 1) / NO_PARALLELS ))

# Calculate files per parallel (ensure we handle all files)
NO_FILES_PER_PARALLEL=$(( (NO_FILES + NO_PARALLELS - 1) / NO_PARALLELS ))

# Decide to split the parallel runs based on NO_RUNS_PER_PARALLEL or NO_FILES_PER_PARALLEL
SPLIT_BY_RUNS=false
SPLIT_BY_FILES=true

# if either of SPLIT_BY_RUNS or SPLIT_BY_FILES is true, use that setting. Otherwise, use the default setting.
if [ $SPLIT_BY_RUNS = false ] && [ $SPLIT_BY_FILES = false ]; then
    # if both are false, use the default setting
    if [ $NO_RUNS_PER_PARALLEL -gt 0 ]; then
        SPLIT_BY_RUNS=true
        echo "Splitting by runs: Running $NO_PARALLELS * $NO_RUNS_PER_PARALLEL runs per parallel"
    else
        SPLIT_BY_FILES=true
        echo "Splitting by files: Running $NO_PARALLELS * $NO_FILES_PER_PARALLEL files per parallel"
    fi
fi

# Run the scripts in parallel and capture their exit status
PIDS=()
STATUSES=()
MEMORY_MONITOR_PIDS=()

if [ $SPLIT_BY_RUNS = true ]; then
    for NOTES_FILE in "${NOTES_FILES_ARRAY[@]}"; do
        # outdir is named according to the subdirectory of the notes file
        # concat the subdirectory name with an absolute path, and the file prefix
        ABS_OUTDIR="synthetic_data/2025-07-10_results/raw_output"
        FILENAME=$(basename "$NOTES_FILE" .tsv)
        f_prefix=${FILENAME%-notes-00000}
        OUTDIR="$ABS_OUTDIR/$(basename "$(dirname "$NOTES_FILE")")/$f_prefix"

        for i in $(seq 0 $((NO_PARALLELS-1))); do
            START=$((i*NO_RUNS_PER_PARALLEL))
            END=$(((i+1)*NO_RUNS_PER_PARALLEL))
            # Ensure we don't exceed the total number of runs
            if [ $END -gt $NO_RUNS_PER_FILE ]; then
                END=$NO_RUNS_PER_FILE
            fi
            
            # Create unique identifier for this process
            PROCESS_ID="runs_${i}_$(basename "$NOTES_FILE" .tsv)"
            MEMORY_LOG_FILE="$MEMORY_LOG_DIR/memory_${PROCESS_ID}.csv"
            
            echo "** Running synthetic_data/2025-07-10_results/run_multiple_times.sh $NOTES_FILE $OUTDIR $START $END **"
            synthetic_data/2025-07-10_results/run_multiple_times.sh "$NOTES_FILE" "$OUTDIR" "$START" "$END" &
            PROCESS_PID=$!
            PIDS+=($PROCESS_PID)
            
            # Start memory monitoring for this process
            monitor_memory "$PROCESS_PID" "$MEMORY_LOG_FILE" "$PROCESS_ID" &
            MEMORY_MONITOR_PIDS+=($!)
        done
    done
else
    # split the files in the dataset into chunks of NO_PARALLELS jobs, and allocate a CPU core to each chunk
    # echo "** notes files: ${NOTES_FILES_ARRAY[*]}"
    for i in $(seq 0 $((NO_PARALLELS-1))); do
        JOB_START=$((i*NO_FILES_PER_PARALLEL))
        JOB_END=$(((i+1)*NO_FILES_PER_PARALLEL))
        if [ $JOB_END -gt $NO_FILES ]; then
            JOB_END=$NO_FILES
        fi
        # get the list of files for this parallel job as an array
        NOTES_FILES_FOR_PARALLEL=("${NOTES_FILES_ARRAY[@]:JOB_START:NO_FILES_PER_PARALLEL}")
        
        # echo "JOB_START: $JOB_START - JOB_END: $JOB_END"
        # echo "NOTES_FILES_FOR_PARALLEL: ${NOTES_FILES_FOR_PARALLEL[*]}"
        
        # Create unique identifier for this parallel chunk
        PROCESS_ID="files_chunk_${i}"
        MEMORY_LOG_FILE="$MEMORY_LOG_DIR/memory_${PROCESS_ID}.csv"
        
        # Run this chunk as a single background process that processes files sequentially
        (
            echo "** Starting parallel chunk $i with ${#NOTES_FILES_FOR_PARALLEL[@]} files **"
            for NOTES_FILE in "${NOTES_FILES_FOR_PARALLEL[@]}"; do
                # echo "Processing file: $NOTES_FILE"
                # get the outdir for the file
                ABS_OUTDIR="synthetic_data/2025-07-10_results/raw_output"
                FILENAME=$(basename "$NOTES_FILE" .tsv)
                f_prefix=${FILENAME%-notes-00000}
                OUTDIR="$ABS_OUTDIR/$(basename "$(dirname "$NOTES_FILE")")/$f_prefix"
                echo "Processing file: $NOTES_FILE"
                START=0
                END=$NO_RUNS_PER_FILE
                # echo "* Running synthetic_data/2025-07-10_results/run_multiple_times.sh $NOTES_FILE $OUTDIR $START $END"
                # echo "** run_multiple_times.sh NOTE_FILE: $NOTES_FILE"
                # echo "** run_multiple_times.sh PARENT_OUTDIR: $OUTDIR"
                # echo "** run_multiple_times.sh START: $START"
                # echo "** run_multiple_times.sh END: $END"
                synthetic_data/2025-07-10_results/run_multiple_times.sh "$NOTES_FILE" "$OUTDIR" "$START" "$END"
            done
            echo "** Finished parallel chunk $i **"
        ) &
        PROCESS_PID=$!
        PIDS+=($PROCESS_PID)
        
        # Start memory monitoring for this process
        monitor_memory "$PROCESS_PID" "$MEMORY_LOG_FILE" "$PROCESS_ID" &
        MEMORY_MONITOR_PIDS+=($!)
    done
fi

# Wait for jobs to finish
FAIL=0
for pid in "${PIDS[@]}"; do
    wait $pid
    STATUS=$?
    STATUSES+=($STATUS)
    if [ $STATUS -ne 0 ]; then
        FAIL=1
    fi
done

# Wait for memory monitoring processes to finish
for monitor_pid in "${MEMORY_MONITOR_PIDS[@]}"; do
    wait $monitor_pid 2>/dev/null || true
done

echo "Exit statuses: ${STATUSES[@]}"
echo "Memory logs saved to: $MEMORY_LOG_DIR"
exit $FAIL