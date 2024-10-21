import argparse

from thames_tidal_helper.client import Client


def define_parser():
    parser = argparse.ArgumentParser(description="Thames Tidal Data Helper")
    parser.add_argument(
        "--input", type=str, default="input.txt", help="Path to the input file"
    )
    parser.add_argument(
        "--output", type=str, default="output.txt", help="Path to the output file"
    )
    parser.add_argument(
        "--site",
        type=str,
        default="Chelsea Bridge",
        help="Site name for tidal data. See the README for options.",
    )
    parser.add_argument(
        "--cache", type=str, default="./.cache/", help="Path to the cache directory"
    )
    parser.add_argument(
        "--silent", action="store_true", help="Suppress output to console"
    )

    return parser


def main():
    parser = define_parser()
    args = parser.parse_args()
    client = Client(
        input_file=args.input,
        output_file=args.output,
        site=args.site,
        cache_path=args.cache,
    )
    client.run()


if __name__ == "__main__":
    main()
