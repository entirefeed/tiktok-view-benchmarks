# TikTok view benchmarks

This repository holds the distribution of views across 2,785,427,819 public TikTok posts published from October 2024 to September 2026, for all posts together and for 4,038 hashtags. Use it to see how many views a normal TikTok post gets, and where one post or one account sits against the rest.

Check any account against this data: https://entirefeed.com/tools/tiktok-benchmark

## Headline numbers

| All public posts in the data | |
|---|---:|
| Posts counted | 2,785,427,819 |
| Median views | 401 |
| Share of posts under 1,000 views | 77.6% |
| Top 10% starts at | 2,650 views |
| Top 5% starts at | 8,361 views |
| Top 1% starts at | 116,227 views |
| Share of posts with 100,000 views or more | 1.1% |

Half of all posts get 401 views or fewer. A post with 2,650 views is already ahead of nine posts in ten.

These are medians and percentiles, not averages. A small number of very large posts pull the average far above what a normal post gets, so the median is the better answer to "how many views does a TikTok post get".

Videos and photo posts are close in the middle and far apart at the top:

| Format | Posts counted | Median views | Top 10% starts at | Top 1% starts at |
|---|---:|---:|---:|---:|
| Video | 2,564,613,877 | 398 | 2,815 | 126,725 |
| Photo | 220,813,942 | 430 | 1,555 | 22,558 |

## By hashtag

Twenty well-known hashtags, sorted by posts counted. All 4,038 are in [`data/benchmarks_by_hashtag.csv`](data/benchmarks_by_hashtag.csv).

| Hashtag | Posts counted | Median views | Top 10% starts at |
|---|---:|---:|---:|
| #viral | 113,489,683 | 629 | 5,322 |
| #funny | 23,034,612 | 703 | 6,496 |
| #fyp | 17,137,301 | 985 | 30,447 |
| #tiktokshop | 15,627,767 | 505 | 2,994 |
| #booktok | 8,912,020 | 384 | 2,013 |
| #music | 8,416,376 | 494 | 4,292 |
| #gym | 8,286,079 | 611 | 3,128 |
| #dance | 7,294,098 | 728 | 6,069 |
| #gaming | 6,969,676 | 516 | 5,463 |
| #makeup | 5,883,666 | 564 | 4,827 |
| #dog | 5,021,731 | 465 | 2,515 |
| #travel | 4,955,079 | 555 | 4,006 |
| #fitness | 4,700,076 | 497 | 2,742 |
| #fashion | 4,643,917 | 605 | 5,527 |
| #skincare | 3,950,566 | 493 | 3,902 |
| #comedy | 3,855,177 | 670 | 11,282 |
| #food | 3,517,429 | 602 | 8,846 |
| #smallbusiness | 3,469,270 | 440 | 2,532 |
| #podcast | 2,474,809 | 602 | 4,782 |
| #recipe | 600,795 | 868 | 29,928 |

The hashtag changes the answer. The top 10% starts at 2,013 views for #booktok and at 29,928 for #recipe, so compare a post with posts on the same topic.

## Files

| File | What it holds |
|---|---|
| [`data/distributions.json`](data/distributions.json) | The raw histograms: all posts, videos, photo posts, and one histogram per hashtag. This is the file the free tool reads. |
| [`data/benchmarks_overall.csv`](data/benchmarks_overall.csv) | Three rows: all posts, videos, photo posts. |
| [`data/benchmarks_by_hashtag.csv`](data/benchmarks_by_hashtag.csv) | One row per hashtag, sorted by posts counted. |
| [`scripts/build_tables.py`](scripts/build_tables.py) | Builds both CSV files from the JSON. |
| [`scripts/percentile.py`](scripts/percentile.py) | Prints the percentile of a view count. |

Both CSV files have the same columns:

| Column | Meaning |
|---|---|
| `posts_counted` | Posts in the group. This count is exact. |
| `p10_views`, `p25_views`, `median_views`, `p75_views`, `p90_views`, `p95_views`, `p99_views` | Views at that percentile. `p90_views` is where the top 10% starts. |
| `pct_under_1000` | Share of posts with fewer than 1,000 views, in percent. |
| `pct_10000_or_more`, `pct_100000_or_more` | Share of posts with at least that many views, in percent. |

## How to use it

The scripts need Python 3 and nothing else.

```
python3 scripts/percentile.py 5000
python3 scripts/percentile.py 5000 --hashtag podcast
python3 scripts/build_tables.py
```

The first command prints `5,000 views is more than 93.1% of all public TikTok posts in the data (2,785,427,819 posts counted).`

### Python: percentile of a view count

```python
import json
import math

with open("data/distributions.json", encoding="utf-8") as f:
    data = json.load(f)


def percentile(histogram, views):
    """Share of posts with fewer views, 0 to 100."""
    first_bin, counts = histogram
    position = math.log10(views + 1) * data["binsPerDecade"]
    below = 0.0
    for i, count in enumerate(counts):
        if first_bin + i + 1 <= position:
            below += count
        elif first_bin + i <= position:
            below += count * (position - first_bin - i)
    return 100 * below / sum(counts)


print(round(percentile(data["all"]["any"], 5000), 1))  # 93.1, among all posts
print(round(percentile(data["tags"]["podcast"], 5000), 1))  # 90.3, among #podcast posts
```

### JavaScript: median and top 10% for a hashtag

```js
import { readFileSync } from "node:fs";

const data = JSON.parse(readFileSync("data/distributions.json", "utf8"));

// Views at quantile q (0 to 1). 0.5 is the median, 0.9 is where the top 10% starts.
function viewsAt([firstBin, counts], q) {
  const target = q * counts.reduce((sum, n) => sum + n, 0);
  let seen = 0;
  for (let i = 0; i < counts.length; i++) {
    if (counts[i] > 0 && seen + counts[i] >= target) {
      const position = firstBin + i + (target - seen) / counts[i];
      return Math.round(10 ** (position / data.binsPerDecade) - 1);
    }
    seen += counts[i];
  }
}

console.log(viewsAt(data.tags.podcast, 0.5)); // 602
console.log(viewsAt(data.tags.podcast, 0.9)); // 4782
```

### Reading the CSV

```python
import csv

with open("data/benchmarks_by_hashtag.csv", encoding="utf-8", newline="") as f:
    rows = {row["hashtag"]: row for row in csv.DictReader(f)}

row = rows["podcast"]
print(row["posts_counted"], row["median_views"], row["p90_views"])  # 2474809 602 4782
```

## Method

**Window.** Posts published from October 2024 to September 2026, which is 24 complete months.

**One view count per post.** Each post has one view count: the number the source dataset recorded the last time it read the post. This is not a daily history.

**The 7-day minimum.** A post is counted only if it was at least 7 days old when its views were read. New posts are still gaining views, so counting them would make every number here look lower than it is. The free tool applies the same rule to the account it checks.

**Binning.** Views are grouped into bins on a log scale, 20 bins for each factor of ten: `bin = floor(log10(views + 1) * 20)`. Each bin is about 12% wide. In `distributions.json` a histogram is `[firstBin, counts]`, where `counts[i]` is the number of posts in bin `firstBin + i`.

**Percentiles.** A percentile is the share of posts with fewer views. To read a value inside a bin, the scripts draw a straight line across the bin on the log scale. Post counts are exact. View figures are estimates that are right to within one bin, so read 401 as "about 400".

**Hashtags.** Hashtags are lower-case. Only the first 10 hashtags of a post are read. A post that carries several listed hashtags is counted once under each, so the hashtag rows overlap and do not add up to the total. A hashtag is counted in a month only if it had at least 500 counted posts that month, and it is listed only if it has at least 1,000 counted posts across the window. Videos and photo posts are counted together.

**What is included.** Public videos and photo posts from every country and language in the source. Ads, paid partnerships and TikTok Shop posts are not removed.

**What is not included.** There is no post, account or user data here: no post IDs, handles, captions or links. There are no likes, comments, shares, saves or engagement rates either. This data is about views only.

## Limits and known biases

- **The source is a scrape, not a TikTok export.** It holds the posts its collector found. We did not collect it and we cannot check how complete it is. We do not know what share of all TikTok posts it covers, or whether some countries, languages or account sizes are thinner than others. Read every number as "among the posts in this data".
- **Posts were read at different ages.** A post may have been read at 8 days old or at a year old. Older posts have had more time to collect views.
- **Posts that were deleted or made private before the source read them are missing.**
- **Every post counts once.** An account that posts ten times a day weighs more than an account that posts once a week. These are benchmarks for posts, not for accounts.
- **The hashtag list is a fixed list of 4,038.** It is not every hashtag on TikTok and it is not a strict top 4,038. Judging by the names, it leans towards English and Spanish and towards the United States. The list we work from has 4,180 names. We left out the 138 with fewer than 60,000 posts counted, because their top percentiles rest on too few posts, and 4 names we chose not to publish.
- **`posts_counted` is not a hashtag's size on TikTok.** It is the number of posts in this data that carry the hashtag in their first 10 hashtags, in the months that passed the 500-post rule.
- **Small hashtags are less reliable.** The smallest hashtag here has 60,199 posts counted, so its top 1% is about 600 posts.
- **Posts with a listed hashtag do better than posts overall.** 3,506 of the 4,038 hashtags have a median at or above the overall median of 401. Compare a hashtag with other hashtags, not only with the overall row.
- **A hashtag does not cause views.** These numbers describe the posts that used a hashtag. They do not say what adding the hashtag would do for a post.
- **A view is whatever TikTok counts as a view.**

## Source and attribution

The numbers are aggregated from [TikTok Videos (5.6 billion)](https://huggingface.co/datasets/datasocial/tiktok-5.6B-videos) by DataSocial, published on Hugging Face under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/). We changed it by counting posts into view bins, overall and for each hashtag. No row of the source dataset is reproduced here. DataSocial has not reviewed or endorsed this repository. Neither DataSocial nor EntireFeed is affiliated with TikTok.

## How to cite

Quoting numbers from this repository in an article, report or paper is welcome. Please cite it like this:

> EntireFeed (2026). TikTok View Benchmarks: the distribution of views across 2.8 billion public TikTok posts, October 2024 to September 2026. https://github.com/entirefeed/tiktok-view-benchmarks

```bibtex
@misc{entirefeed2026tiktokviews,
  author       = {{EntireFeed}},
  title        = {TikTok View Benchmarks: the distribution of views across 2.8 billion public TikTok posts},
  year         = {2026},
  howpublished = {\url{https://github.com/entirefeed/tiktok-view-benchmarks}},
  note         = {Posts published from October 2024 to September 2026. Source data: DataSocial, TikTok Videos (5.6 billion), CC BY-NC 4.0}
}
```

GitHub also reads [`CITATION.cff`](CITATION.cff): use "Cite this repository" in the sidebar.

## Licence

- The scripts are under the [MIT licence](LICENSE).
- The data files in `data/` are under [CC BY-NC 4.0](LICENSE-DATA), the same licence as the source dataset. You may copy and adapt them for non-commercial purposes if you credit both EntireFeed and DataSocial. For commercial use of the underlying dataset, contact DataSocial.

Published by [EntireFeed](https://entirefeed.com). Check any account against this data: https://entirefeed.com/tools/tiktok-benchmark
