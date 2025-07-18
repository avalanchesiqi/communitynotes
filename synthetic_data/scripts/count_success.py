#!/usr/bin/env python3
"""
Script to count successful runs in each subdirectory.
A run is considered successful if it has both scored_notes.tsv and helpfulness_scores.tsv files.
"""

import os
import glob
from pathlib import Path


def count_successful_runs(directory):
    """Count successful runs in a given directory."""
    successful_count = 0
    total_count = 0

    # Find all run directories
    run_dirs = glob.glob(os.path.join(directory, "run_*"))

    for run_dir in run_dirs:
        if os.path.isdir(run_dir):
            total_count += 1

            # Check if both required files exist
            scored_notes_file = os.path.join(run_dir, "scored_notes.tsv")
            helpfulness_scores_file = os.path.join(run_dir, "helpfulness_scores.tsv")

            if os.path.isfile(scored_notes_file) and os.path.isfile(
                helpfulness_scores_file
            ):
                successful_count += 1

    return successful_count, total_count


def main():
    base_dir = "/N/project/community_notes_manip/communitynotes/synthetic_data/2025-07-10_results/raw_output"

    print("Counting successful runs in each subdirectory...")
    print("=" * 60)

    # Get all top-level directories
    top_level_dirs = [
        d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))
    ]

    for top_dir in sorted(top_level_dirs):
        top_path = os.path.join(base_dir, top_dir)
        print(f"\n{top_dir}:")
        print("-" * len(top_dir))

        # Get all subdirectories in the top-level directory
        subdirs = [
            d for d in os.listdir(top_path) if os.path.isdir(os.path.join(top_path, d))
        ]

        for subdir in sorted(subdirs):
            subdir_path = os.path.join(top_path, subdir)
            successful, total = count_successful_runs(subdir_path)

            print(f"  {subdir}: {successful}/{total} successful runs")

            # Also print the run numbers for successful runs
            if successful > 0:
                successful_runs = []
                run_dirs = glob.glob(os.path.join(subdir_path, "run_*"))
                for run_dir in run_dirs:
                    if os.path.isdir(run_dir):
                        scored_notes_file = os.path.join(run_dir, "scored_notes.tsv")
                        helpfulness_scores_file = os.path.join(
                            run_dir, "helpfulness_scores.tsv"
                        )

                        if os.path.isfile(scored_notes_file) and os.path.isfile(
                            helpfulness_scores_file
                        ):
                            run_name = os.path.basename(run_dir)
                            successful_runs.append(run_name)

                print(f"    Successful runs: {', '.join(sorted(successful_runs))}")


if __name__ == "__main__":
    main()
