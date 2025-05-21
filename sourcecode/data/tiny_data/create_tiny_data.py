import argparse
import os
from datetime import datetime
import pandas as pd


def extract_subsample(data_dir, end_datetime):
    # convert human readable date to unix timestamp
    end_timestamp = int(
        datetime.strptime(end_datetime, "%Y-%m-%d").timestamp() * 1e3
    )
    print(f"End datetime: {end_datetime}")

    # all notes published before this timestamp will be extracted
    # use pandas to read the tsv file, the first row is the header
    note_df = pd.read_csv(
        os.path.join(data_dir, 'notes-00000.zip'),
        sep="\t",
        header=0,
        encoding="utf-8",
        compression="zip",
    )
    num_note = len(note_df)
    print(f'Total number of notes: {num_note:,}')
    # filter the notes that are published before the end timestamp
    tiny_note_df = note_df[note_df['createdAtMillis'] < end_timestamp]
    # set the summary column to empty string
    tiny_note_df = tiny_note_df.assign(summary='')
    num_tiny_note = len(tiny_note_df)
    print(f'Number of notes before {end_datetime}: {num_tiny_note:,}')
    print(f'Note sampling rate: {num_tiny_note / num_note:.2%}\n')

    # save the filtered notes to a new tsv file
    tiny_note_df.to_csv(
        'tiny-notes-00000.tsv',
        sep="\t",
        index=False,
        encoding="utf-8",
    )
    
    # create an empty dataframe to store the filtered ratings
    all_tiny_rating_df = pd.DataFrame()
    
    # all ratings published before this timestamp will be extracted
    for subdir, _, files in os.walk(os.path.join(data_dir, 'ratings')):
        for f in sorted(files):
            if not f.endswith('.zip'):
                continue
            # read the tsv file, the first row is the header
            rating_df = pd.read_csv(
                os.path.join(subdir, f),
                sep="\t",
                header=0,
                encoding="utf-8",
                compression="zip",
            )
            num_rating = len(rating_df)
            print(f'Total number of ratings: {num_rating:,} in {f}')
            # filter the ratings that are published before the end timestamp
            tiny_rating_df = rating_df[rating_df['createdAtMillis'] < end_timestamp]
            num_tiny_rating = len(tiny_rating_df)
            print(f'Number of partition ratings before {end_datetime}: {num_tiny_rating:,}')
            print(f'Rating sampling rate: {num_tiny_rating / num_rating:.2%}\n')

            # append the filtered ratings to the all_tiny_rating_df
            all_tiny_rating_df = pd.concat([all_tiny_rating_df, tiny_rating_df], ignore_index=True)
        
    print(f'Number of all ratings before {end_datetime}: {len(all_tiny_rating_df):,}')
    # save all filtered ratings to a new tsv file
    all_tiny_rating_df.to_csv(
        'tiny-ratings-00000.tsv',
        sep="\t",
        index=False,
        encoding="utf-8",
    )

    # only extract the first two rows of the status history
    note_status_history_df = pd.read_csv(
        os.path.join(data_dir, 'noteStatusHistory-00000.zip'),
        sep="\t",
        header=0,
        encoding="utf-8",
        compression="zip",
    )
    num_note_note_status_history = len(note_status_history_df)
    print(f'Total number of notes with status history: {num_note_note_status_history:,}')
    # create a new dataframe with the same columns as note_status_history_df
    tiny_note_status_history_df = note_status_history_df.head(1)
    # create a dummy row and set noteId to 1
    for col in note_status_history_df.columns:
        if col == 'noteId':
            tiny_note_status_history_df[col] = 1
    
    num_tiny_note_status_history = len(tiny_note_status_history_df)
    print(f'Note Status History sampling rate: {num_tiny_note_status_history / num_note_note_status_history:.2%}\n')

    # save the filtered note status history to a new tsv file
    tiny_note_status_history_df.to_csv(
        'tiny-noteStatusHistory-00000.tsv',
        sep="\t",
        index=False,
        encoding="utf-8",
    )

    # copy the whole userEnrollment-00000.tsv file
    user_enrollment_df = pd.read_csv(
        os.path.join(data_dir, 'userEnrollment-00000.zip'),
        sep="\t",
        header=0,
        encoding="utf-8",
        compression="zip",
    )
    num_user_enrollment = len(user_enrollment_df)
    print(f'Total number of user enrollment: {num_user_enrollment:,}')

    # save the filtered user enrollment to a new tsv file
    user_enrollment_df.to_csv(
        'userEnrollment-00000.tsv',
        sep="\t",
        index=False,
        encoding="utf-8",
    )
    print(f'Copy and unzip userEnrollment-00000.zip to current directory')


if __name__ == "__main__":
    # use argparse to parse the command line arguments
    parser = argparse.ArgumentParser(description="Take data directory and end datetime from argparse")
    parser.add_argument(
        "-d",
        "--data_dir",
        type=str,
        required=True,
        help="Target directory of Community Notes data",
    )
    parser.add_argument(
        "-e",
        "--end_datetime",
        type=str,
        required=True,
        help="End datetime for extracting subsample (format: YYYY-MM-DD)",
    )

    args = parser.parse_args()
    data_dir = args.data_dir
    end_datetime = args.end_datetime

    extract_subsample(data_dir, end_datetime)
