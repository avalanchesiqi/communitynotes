#!/usr/bin/env python3
"""
Community Notes Helpfulness Score Calculator

This script calculates groundtruth and inferred helpfulness scores according to the Community Notes guide rules.

Rules:
- Groundtruth helpfulness: i_n > 0.4 AND |f_n| < 0.5
- Inferred helpfulness: coreNoteIntercept > 0.4 AND |coreNoteFactor1| < 0.5

To run scrip:
source /N/project/community_notes_manip/communitynotes/.venv/bin/activate
python /N/project/community_notes_manip/communitynotes/synthetic_data/2025-07-10_results/count_FP_FN.py
"""

import pandas as pd
import numpy as np
import os
import glob
import re
from pathlib import Path
import tqdm
import logging
import sys
from datetime import datetime


# Set up logging to capture all print statements
def setup_logging(log_dir):
    """Set up logging to capture all print statements to both console and file."""
    # Create logs directory if it doesn't exist
    # log_dir = "running_logs"
    os.makedirs(log_dir, exist_ok=True)

    # Create a custom logger
    logger = logging.getLogger("count_fp_logger")
    logger.setLevel(logging.INFO)

    # Remove any existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create formatters
    console_formatter = logging.Formatter("%(message)s")
    file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # File handler
    file_handler = logging.FileHandler(f"{log_dir}/count_fp.log", mode="w")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    # Replace the built-in print function with logger.info
    def custom_print(*args, **kwargs):
        message = " ".join(str(arg) for arg in args)
        logger.info(message)

    # Store original print function and replace it
    global original_print
    original_print = print
    globals()["print"] = custom_print

    return logger


def calculate_helpfulness_score(intercept, factor):
    """
    Calculate helpfulness score based on Community Notes rules:
    - intercept >= 0.4 AND |factor| < 0.5

    Args:
        intercept: The intercept value (i_n or coreNoteIntercept)
        factor: The factor value (f_n or coreNoteFactor1)

    Returns:
        1 if helpful, 0 otherwise
    """
    if intercept > 0.4 and abs(factor) < 0.5:
        return 1
    else:
        return 0


def extract_params_from_filename(filename):
    """
    Extract parameters from filename.
    Expected format: {params}_TrueNoteParams.tsv
    """
    # Extract the part before _TrueNoteParams.tsv
    match = re.search(r"(.+)_TrueNoteParams\.tsv$", filename)
    if match:
        return match.group(1)
    else:
        raise ValueError(f"Could not extract parameters from filename: {filename}")


def main():
    # Initialize logging
    logger = setup_logging(
        log_dir="/N/project/community_notes_manip/communitynotes/synthetic_data/2025-07-10_results/running_logs/count_FP_FN"
    )

    print(f"Starting Community Notes Helpfulness Score Calculator at {datetime.now()}")
    print("=" * 60)

    # Define paths
    abs_path = (
        "/N/project/community_notes_manip/communitynotes/synthetic_data/2025-07-10_data"
    )
    out_dir = "/N/project/community_notes_manip/communitynotes/synthetic_data/2025-07-10_results"
    for subdir in tqdm.tqdm(os.listdir(abs_path), desc="Processing subdirectories"):
        out_path = os.path.join(out_dir, "ground_truth", subdir)  #
        results_path = os.path.join(out_dir, "raw_output", subdir)
        # Create output directory if it doesn't exist
        os.makedirs(out_path, exist_ok=True)

        print(f"Input path: {abs_path}")
        print(f"Output path: {out_path}")
        print(f"Results path: {results_path}")

        # Find all TrueNoteParams files
        true_note_params_files = glob.glob(
            os.path.join(abs_path, subdir, "*_TrueNoteParams.tsv")
        )
        print(f"Found {len(true_note_params_files)} TrueNoteParams files")

        # Initialize results dataframe with additional columns
        """
        A given note thus has two labels,
        - the label it is given by the algorithm (uppercase), helpful, H, or unhelpful, U
        - the label it should receive based on its true parameters (lowercase), helpful, h, or unhelpful, u.

        We are interested in the following:
        - False positives for helpful notes: the ones that are classified as helpful but are actually unhelpful (n_Hu)
        - False negatives for helpful notes: the ones that are classified as unhelpful but are actually helpful (n_hU)
=
        """
        FP_count_df = pd.DataFrame(
            columns=[
                "params",
                "run_result_dir",
                "n_H",
                "n_U",
                "n_h",
                "n_u",
                "p_u_H",
                "p_h_U",
                "p_H_u",
                "p_U_h",
            ]
        )

        for file_path in true_note_params_files:
            filename = os.path.basename(file_path)
            params = extract_params_from_filename(filename)

            print(f"\nProcessing file: {filename}")
            print(f"Parameters: {params}")

            # Read the TrueNoteParams file
            df = pd.read_csv(file_path, sep="\t")
            print(f"Original data shape: {df.shape}")
            print(f"Original columns: {list(df.columns)}")

            # Calculate groundtruth helpfulness
            df["ground_helpfulness"] = df.apply(
                lambda row: calculate_helpfulness_score(
                    row["RealNoteIntercept"], row["RealNoteFactor"]
                ),
                axis=1,
            )

            # Add parameters column
            df["parameters"] = params

            # Save groundtruth helpfulness file
            groundtruth_output_path = os.path.join(
                out_path, f"{params}_TrueHelpfulness.tsv"
            )
            df.to_csv(groundtruth_output_path, sep="\t", index=False)

            print(f"Groundtruth helpfulness saved to: {groundtruth_output_path}")
            print(f"Groundtruth data head:")
            print(df.head())

            # Process corresponding results folders
            # FNR = FN / (FN + TP) # proportion of actual positives that are incorrectly classified as negative
            # FPR = FP / (FP + TN) # proportion of actual negatives that are incorrectly classified as positive
            # False positives for unhelpful notes are the ones that are classified as unhelpful but are actually helpful
            # False negatives for unhelpful notes are the ones that are classified as helpful but are actually unhelpful

            if os.path.exists(results_path):
                run_folders = glob.glob(os.path.join(results_path, f"{params}/run_*"))
                print(f"Found {len(run_folders)} run folders for parameters {params}")
                print(f"glob command: {os.path.join(results_path, f'{params}/run_*')}")
                for run_folder in tqdm.tqdm(
                    run_folders,
                    desc=f"Processing {len(run_folders)} run folders for parameters {params}",
                ):
                    scored_notes_path = os.path.join(run_folder, "scored_notes.tsv")

                    if os.path.exists(scored_notes_path):
                        # Read scored notes
                        scored_df = pd.read_csv(scored_notes_path, sep="\t")
                        print(f"Scored notes shape: {scored_df.shape}")

                        full_len = len(scored_df)
                        # remove rows with nan for coreNoteIntercept	coreNoteFactor1
                        scored_df = scored_df.dropna(
                            subset=[
                                "coreNoteIntercept",
                                "coreNoteFactor1",
                            ]
                        )
                        print(
                            f"Exclude notes with no helpfulness score ({full_len-len(scored_df)}), retained {np.round(len(scored_df)/full_len*100, 2)}% ({len(scored_df)} records)"
                        )

                        # Calculate inferred helpfulness
                        scored_df["inferred_helpfulness"] = scored_df.apply(
                            lambda row: calculate_helpfulness_score(
                                row["coreNoteIntercept"], row["coreNoteFactor1"]
                            ),
                            axis=1,
                        )

                        # Merge with groundtruth data
                        merged_df = pd.merge(
                            df,
                            scored_df[["noteId", "inferred_helpfulness"]],
                            on="noteId",
                            how="inner",
                        )

                        ## Helpful notes: get FP and FN
                        # In our case, False positives for helpful notes are the ones that are classified as helpful but are actually unhelpful
                        # False negatives for helpful notes are the ones that are classified as unhelpful but are actually helpful
                        merged_df["n_uH"] = np.where(
                            (merged_df["ground_helpfulness"] == 0)
                            & (merged_df["inferred_helpfulness"] == 1),
                            1,
                            0,
                        )

                        merged_df["n_hU"] = np.where(
                            (merged_df["ground_helpfulness"] == 1)
                            & (merged_df["inferred_helpfulness"] == 0),
                            1,
                            0,
                        )

                        # Count false positives and false negatives
                        n_uH = merged_df["n_uH"].sum()
                        n_hU = merged_df["n_hU"].sum()

                        # Count helpful and unhelpful ground truth
                        n_h = (merged_df["ground_helpfulness"] == 1).sum()
                        n_u = len(merged_df) - n_h

                        # Count inferred helpfulness
                        n_H = (merged_df["inferred_helpfulness"] == 1).sum()
                        n_U = len(merged_df) - n_H

                        # Calculate rates (avoid division by zero)
                        p_u_H = n_uH / n_H if n_H > 0 else 0
                        p_h_U = n_hU / n_U if n_U > 0 else 0
                        p_H_u = n_uH / n_u if n_u > 0 else 0
                        p_U_h = n_hU / n_h if n_h > 0 else 0

                        # Add row to FP_count_df
                        new_row = pd.DataFrame(
                            {
                                "params": [params],
                                "run_result_dir": [run_folder],
                                "n_H": [n_H],
                                "n_U": [n_U],
                                "n_h": [n_h],
                                "n_u": [n_u],
                                "p_u_H": [p_u_H],
                                "p_h_U": [p_h_U],
                                "p_H_u": [p_H_u],
                                "p_U_h": [p_U_h],
                            }
                        )

                        FP_count_df = pd.concat(
                            [FP_count_df, new_row], ignore_index=True
                        )

                        print(f"Merged data head:")
                        print(merged_df.head())

                    else:
                        print(f"Warning: scored_notes.tsv not found in {run_folder}")
            else:
                print(f"Warning: Results path not found: {results_path}")

            # Save FP/FN count results for this parameter set
            param_fp_results_path = os.path.join(
                results_path, params, "FP_FN_count_full.csv"
            )
            os.makedirs(os.path.dirname(param_fp_results_path), exist_ok=True)

            # Filter results for current parameters
            param_results = FP_count_df[FP_count_df["params"] == params]
            if not param_results.empty:
                param_results.to_csv(param_fp_results_path, index=False)
                print(f"FP/FN count results saved to: {param_fp_results_path}")
                print(f"Parameter results head:")
                print(param_results.head())

        # Display final results
        print("\n" + "=" * 50)
        print("FINAL RESULTS SUMMARY")
        print("=" * 50)
        print(f"Total parameter sets processed: {len(true_note_params_files)}")
        print(f"Total runs processed: {len(FP_count_df)}")
        print("\nFP_count_df head:")
        print(FP_count_df.head(10))
        print("\nFP_count_df summary:")
        print(FP_count_df.describe())

        print("\n" + "=" * 60)
        print(f"Script completed at {datetime.now()}")
        print("=" * 60)


if __name__ == "__main__":
    main()
