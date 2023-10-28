import argparse
from itolparser.version import __version__, __author__, __description__
from pathlib import Path
import logging


def get_args():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description=__description__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    main_args = parser.add_argument_group("Main arguments")
    main_args.add_argument(
        "-i",
        "--input",
        help="Input table with categorical metadata in .tsv format unless otherwise specified",
        type=Path,
        required=True,
    )
    main_args.add_argument(
        "-o",
        "--outdir",
        default="itolparser_output",
        metavar="OUTDIR",
        help="Output directory to write files to",
        type=Path,
    )
    main_args.add_argument(
        "--tsv",
        action="store_true",
        help="Force input parsing as .tsv file",
    )
    main_args.add_argument(
        "--csv",
        action="store_true",
        help="Force input parsing as .csv file",
    )
    main_args.add_argument(
        "-v",
        "--version",
        help="prints program version and exits",
        action="version",
        version=__version__,
    )

    formatting_args = parser.add_argument_group("Formatting arguments")
    formatting_args.add_argument(
        "--margin",
        default=5,
        metavar="INT",
        help="Size of margin specified in iTOL file",
        type=int,
    )
    formatting_args.add_argument(
        "--stripwidth",
        default=50,
        metavar="INT",
        help="Strip width specified in iTOL file",
        type=int,
    )
    formatting_args.add_argument(
        "--maxcategories",
        default=18,
        metavar="INT",
        help='Maximum number of categories to not get assigned to "other"',
        type=int,
    )
    formatting_args.add_argument(
        "--ignore",
        help="List of columns to ignore",
        type=str,
        nargs="+",
    )
    formatting_args.add_argument(
        "--continuous",
        help="Comma-separated list of columns to parse as continuous",
        type=str,
        nargs="+",
    )
    formatting_args.add_argument(
        "--palette",
        help="Color palette to use for continuous columns",
        type=str,
        default="GnBu",
    )

    args = parser.parse_args()

    return args


def validate_args(args):
    if args.tsv & args.csv:
        raise ValueError("Please choose either --tsv or --csv, not both.")


def select_input_type(args):
    if args.tsv:
        delim = "\t"
    elif args.csv:
        delim = ","
    else:
        logging.info("No delimiter specified, trying to infer from file extension")
        if args.input.suffix == ".tsv":
            delim = "\t"
        elif args.input.suffix == ".csv":
            delim = ","
        else:
            logging.warning(
                "Could not infer delimiter from file extension, letting pandas.read_csv guess"
            )
            delim = None
    return delim
