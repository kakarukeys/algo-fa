import argparse, sys

from fa.util import transpose_csv


""" Example usage

to recursively transpose all files under current directory to a transposed directory:
find -mindepth 1 -type d -exec mkdir -p transposed/{} \;
find -type f -exec python /home/kakarukeys/projects/algo-fa/tools/transpose_csv.py -o transposed/{} {} \;

to transpose again all transposed files, overwriting the original files:
cd transposed/
find -type f -exec python /home/kakarukeys/projects/algo-fa/tools/transpose_csv.py -o ../{} {} \;

"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tranpose a csv file.")

    parser.add_argument("--sep", default='|', help="Separator (default: %(default)s)")
    parser.add_argument(
        "-o", "--output", type=argparse.FileType('w'), default=sys.stdout,
        help="Output file (default: STDOUT)"
    )
    parser.add_argument("csv_file", type=argparse.FileType('r'), help="csv file to transpose")

    args = parser.parse_args()
    transpose_csv(args.csv_file, args.output, args.sep)
