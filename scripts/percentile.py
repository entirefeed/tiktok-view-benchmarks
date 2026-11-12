"""Print the percentile of a view count, among all posts or among one hashtag.

Run from the repository root:

    python scripts/percentile.py 5000
    python scripts/percentile.py 5000 --hashtag podcast

The percentile is the share of posts in the data with fewer views. Standard
library only.
"""

import argparse
import difflib
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "data", "distributions.json")


def percentile_of(histogram, views, bins_per_decade):
    """Share of posts with fewer views than `views`, 0 to 100."""
    first_bin, counts = histogram
    position = math.log10(max(views, 0) + 1) * bins_per_decade
    below = 0.0
    for i, count in enumerate(counts):
        bin_index = first_bin + i
        if bin_index + 1 <= position:
            below += count
        elif bin_index <= position:
            below += count * (position - bin_index)
        else:
            break
    return 100 * below / sum(counts)


def main():
    parser = argparse.ArgumentParser(description="Percentile of a TikTok view count.")
    parser.add_argument("views", type=int, help="view count of one post, for example 5000")
    parser.add_argument("--hashtag", help="compare with posts that carry this hashtag, for example podcast")
    args = parser.parse_args()
    if args.views < 0:
        sys.exit("views must be 0 or more")

    with open(SOURCE, encoding="utf-8") as f:
        data = json.load(f)

    if args.hashtag:
        tag = args.hashtag.lstrip("#").lower()
        if tag not in data["tags"]:
            close = difflib.get_close_matches(tag, list(data["tags"]), n=5)
            hint = f" Close matches: {', '.join(close)}." if close else ""
            sys.exit(f"#{tag} is not one of the {len(data['tags']):,} hashtags in the data.{hint}")
        histogram, group = data["tags"][tag], f"posts tagged #{tag}"
    else:
        histogram, group = data["all"]["any"], "all public TikTok posts in the data"

    share = percentile_of(histogram, args.views, data["binsPerDecade"])
    print(f"{args.views:,} views is more than {share:.1f}% of {group} ({sum(histogram[1]):,} posts counted).")


if __name__ == "__main__":
    main()
