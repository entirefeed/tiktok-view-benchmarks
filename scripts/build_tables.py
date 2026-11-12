"""Build the CSV tables in data/ from data/distributions.json.

Run from the repository root:

    python scripts/build_tables.py

Standard library only. The percentile and quantile functions use the same
interpolation as the free tool at https://entirefeed.com/tools/tiktok-benchmark:
linear inside a bin on the log scale.
"""

import csv
import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(ROOT, "data", "distributions.json")
OVERALL = os.path.join(ROOT, "data", "benchmarks_overall.csv")
BY_HASHTAG = os.path.join(ROOT, "data", "benchmarks_by_hashtag.csv")

QUANTILES = [
    ("p10_views", 0.10),
    ("p25_views", 0.25),
    ("median_views", 0.50),
    ("p75_views", 0.75),
    ("p90_views", 0.90),
    ("p95_views", 0.95),
    ("p99_views", 0.99),
]
COLUMNS = (
    ["posts_counted"]
    + [name for name, _ in QUANTILES]
    + ["pct_under_1000", "pct_10000_or_more", "pct_100000_or_more"]
)


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


def views_at_quantile(histogram, q, bins_per_decade):
    """Views at quantile q (0 to 1). The inverse of percentile_of."""
    first_bin, counts = histogram
    target = q * sum(counts)
    seen = 0
    for i, count in enumerate(counts):
        if count > 0 and seen + count >= target:
            position = first_bin + i + (target - seen) / count
            return round_half_up(10 ** (position / bins_per_decade) - 1)
        seen += count
    return round_half_up(10 ** ((first_bin + len(counts)) / bins_per_decade) - 1)


def round_half_up(x):
    """Round like JavaScript's Math.round, so results match the live tool."""
    return math.floor(x + 0.5)


def summarise(histogram, bins_per_decade):
    row = {"posts_counted": sum(histogram[1])}
    for name, q in QUANTILES:
        row[name] = views_at_quantile(histogram, q, bins_per_decade)
    row["pct_under_1000"] = f"{percentile_of(histogram, 1_000, bins_per_decade):.2f}"
    row["pct_10000_or_more"] = f"{100 - percentile_of(histogram, 10_000, bins_per_decade):.2f}"
    row["pct_100000_or_more"] = f"{100 - percentile_of(histogram, 100_000, bins_per_decade):.2f}"
    return row


def write_csv(path, key, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[key] + COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    with open(SOURCE, encoding="utf-8") as f:
        data = json.load(f)
    bins_per_decade = data["binsPerDecade"]

    # "all" is every post (all.any in the JSON); "video" and "photo" split it by format.
    overall = [
        {"format": label, **summarise(data["all"][key], bins_per_decade)}
        for label, key in (("all", "any"), ("video", "video"), ("photo", "photo"))
    ]
    write_csv(OVERALL, "format", overall)

    by_hashtag = [
        {"hashtag": tag, **summarise(histogram, bins_per_decade)}
        for tag, histogram in data["tags"].items()
    ]
    by_hashtag.sort(key=lambda row: (-row["posts_counted"], row["hashtag"]))
    write_csv(BY_HASHTAG, "hashtag", by_hashtag)

    print(f"{len(overall)} rows -> {os.path.relpath(OVERALL, ROOT)}")
    print(f"{len(by_hashtag)} rows -> {os.path.relpath(BY_HASHTAG, ROOT)}")


if __name__ == "__main__":
    main()
