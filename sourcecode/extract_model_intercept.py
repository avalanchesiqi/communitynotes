import argparse, re


def extract_global_intercept(log_filepath):
    with open(log_filepath, 'r') as fin:
        while True:
            line = fin.readline()
            if not line:
                break
            if line.startswith('INFO:birdwatch.matrix_factorization:Global Intercept:'):
                intercept = float(line.split(':')[-1].strip())
                next_line = fin.readline()
                if 'Final helpfulness-filtered MF elapsed time' in next_line:
                    # extract the word between "INFO:birdwatch.scorer:MF" and "Final helpfulness-filtered MF elapsed time"
                    model = re.search(r'INFO:birdwatch.scorer:MF(.*) Final helpfulness-filtered MF elapsed time', next_line).group(1)
                    print(f'{model} intercept: {intercept}')


if __name__ == '__main__':
    # use argparse to parse the command line arguments
    parser = argparse.ArgumentParser(description="Take log file path from argparse")
    parser.add_argument(
        "-f",
        "--filepath",
        type=str,
        required=True,
        help="Target log file path of Community Notes running log",
    )

    args = parser.parse_args()
    log_filepath = args.filepath
    extract_global_intercept(log_filepath)
