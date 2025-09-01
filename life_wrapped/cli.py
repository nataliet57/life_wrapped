import argparse
from . import io, stats
from life_wrapped.renderers import receipt_text

def main():
    parser = argparse.ArgumentParser("life-wrapped")
    parser.add_argument("file", help="Path to Excel file (.xlsx)")
    parser.add_argument("--out", default="outputs", help="Output folder")
    parser.add_argument("--top", type=int, default=10, help="Top N highlights")
    args = parser.parse_args()

    days = io.load_days_from_excel(args.file)
    months = stats.bucket_by_month(days)
    print("rendering results")
    print(receipt_text.retrieve_results(months, 12, 12, 12))


if __name__ == "__main__":
    main()