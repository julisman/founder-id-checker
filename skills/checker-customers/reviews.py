#!/usr/bin/env python3
"""Tallies what real customers say, for founder-id-checker. Standard library only, no network.

Three inputs, all CSV files the skill fills by reading public pages and by
asking real customers. Nothing is simulated and nothing is invented: every row
is one real listing, one real review or one real answer.

  listings.csv  one row per page where the business is rated, with the rating
                and the review count the page itself shows:
                source,rating,review_count,url
                This is the rating the health check uses. The review sample
                below is read worst-first to find complaints, so its average is
                biased low and is never used as the rating.

  reviews.csv   one row per review read on Google Maps, GoFood, GrabFood,
                ShopeeFood, Shopee, Tokopedia, TikTok or Instagram:
                source,date,stars,theme,quote,url
                (theme is a short code the skill gives the review: rasa, porsi,
                harga, lama, kebersihan, pelayanan, kemasan, ... ; "pujian" for praise)

  survey.csv    one row per customer who used to buy and stopped, asked by
                WhatsApp or in person:
                date,last_bought,reason,would_return,what_brings_back
                (reason is a short code; would_return is ya / mungkin / tidak)

    python3 reviews.py --listings checker/customers/listings.csv --reviews checker/customers/reviews.csv \
                       --survey checker/customers/survey.csv --out checker
    python3 reviews.py --reviews checker/customers/reviews.csv          # any one file alone works

Writes <out>/customers.json (the health check reads its rating) and
<out>/customers-data.md (the tables the skill builds customers.md from).
"""

import argparse
import csv
import json
import os
import re
import sys
from collections import OrderedDict

LISTING_COLS = ("source", "rating", "review_count", "url")
REVIEW_COLS = ("source", "date", "stars", "theme", "quote", "url")
SURVEY_COLS = ("date", "last_bought", "reason", "would_return", "what_brings_back")
PRAISE = "pujian"
THIN = 3
YES = {"ya", "yes", "y", "iya", "mau"}
MAYBE = {"mungkin", "maybe", "nanti", "lihat dulu", "boleh"}
NO = {"tidak", "no", "nggak", "ga", "gak", "enggak", "tdk"}


class DataError(ValueError):
    pass


def _rows(path, cols):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        header = [h.strip().lower() for h in (reader.fieldnames or [])]
        missing = [c for c in cols if c not in header]
        if missing:
            raise DataError("%s is missing the column(s): %s" % (path, ", ".join(missing)))
        out = []
        for i, row in enumerate(reader, 2):
            row = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
            if not any(row.values()):
                continue
            row["_line"] = i
            out.append(row)
        return out


def stars(text, where):
    m = re.match(r"^\s*([0-5](?:[.,]\d)?)", text or "")
    if not m:
        raise DataError("%s: stars must be a number from 1 to 5, not %r" % (where, text))
    v = float(m.group(1).replace(",", "."))
    if not 1 <= v <= 5:
        raise DataError("%s: stars must be from 1 to 5, not %r" % (where, text))
    return v


def tally_listings(rows, path="listings.csv"):
    if not rows:
        raise DataError("%s has no listings" % path)
    out = []
    for r in rows:
        where = "%s line %d" % (path, r["_line"])
        rating = stars(r["rating"], where)
        try:
            n = int(re.sub(r"[.,\s]", "", r["review_count"]))
        except ValueError:
            raise DataError("%s: review_count must be a whole number, not %r" % (where, r["review_count"]))
        if n <= 0:
            raise DataError("%s: review_count must be above 0" % where)
        if not r["url"]:
            raise DataError("%s: every listing needs its link" % where)
        out.append({"source": r["source"] or "?", "rating": rating, "reviews": n, "url": r["url"]})
    total = sum(l["reviews"] for l in out)
    return {"listings": out, "reviews": total,
            "rating_avg": round(sum(l["rating"] * l["reviews"] for l in out) / float(total), 2)}


def tally_reviews(rows, path="reviews.csv"):
    if not rows:
        raise DataError("%s has no reviews" % path)
    by_source = OrderedDict()
    themes = OrderedDict()
    for r in rows:
        where = "%s line %d" % (path, r["_line"])
        s = stars(r["stars"], where)
        theme = (r["theme"] or "").lower()
        if not theme:
            raise DataError("%s: every review needs a theme code (use %r for praise)" % (where, PRAISE))
        if not r["url"]:
            raise DataError("%s: every review needs the link it was read at" % where)
        src = by_source.setdefault(r["source"] or "?", {"reviews": 0, "stars": 0.0})
        src["reviews"] += 1
        src["stars"] += s
        t = themes.setdefault(theme, {"theme": theme, "count": 0, "stars": 0.0, "low": 0, "quotes": []})
        t["count"] += 1
        t["stars"] += s
        if s <= 3:
            t["low"] += 1
        if r["quote"] and len(t["quotes"]) < 2:
            t["quotes"].append({"quote": r["quote"], "stars": s, "source": r["source"], "url": r["url"]})
    n = len(rows)
    total = sum(v["stars"] for v in by_source.values())
    sources = [{"source": k, "reviews": v["reviews"], "rating": round(v["stars"] / v["reviews"], 2)} for k, v in by_source.items()]
    complaints, praise = [], None
    for t in themes.values():
        t["avg_stars"] = round(t["stars"] / t["count"], 2)
        del t["stars"]
        t["thin"] = t["count"] < THIN
        if t["theme"] == PRAISE:
            praise = t
        else:
            complaints.append(t)
    complaints.sort(key=lambda t: (-t["count"], t["avg_stars"]))
    low = sum(1 for r in rows if stars(r["stars"], "") <= 3)
    # sample_rating is the average of the reviews read, which were read worst-first: never a rating
    return {"reviews": n, "sample_rating": round(total / n, 2), "low_star_share": round(low / float(n), 3),
            "sources": sources, "complaints": complaints, "praise": praise}


def _answer(v):
    v = (v or "").strip().lower()
    if v in YES:
        return "ya"
    if v in MAYBE:
        return "mungkin"
    if v in NO:
        return "tidak"
    return None


def tally_survey(rows, path="survey.csv"):
    if not rows:
        raise DataError("%s has no answers" % path)
    reasons = OrderedDict()
    back = OrderedDict()
    ret = {"ya": 0, "mungkin": 0, "tidak": 0}
    for r in rows:
        where = "%s line %d" % (path, r["_line"])
        reason = (r["reason"] or "").lower()
        if not reason:
            raise DataError("%s: every answer needs a reason code" % where)
        a = _answer(r["would_return"])
        if a is None:
            raise DataError("%s: would_return must be ya, mungkin or tidak, not %r" % (where, r["would_return"]))
        ret[a] += 1
        reasons[reason] = reasons.get(reason, 0) + 1
        w = (r["what_brings_back"] or "").strip()
        if w:
            back[w.lower()] = back.get(w.lower(), 0) + 1
    n = len(rows)
    return {"answers": n,
            "reasons": [{"reason": k, "count": v, "share": round(v / float(n), 3), "thin": v < THIN}
                        for k, v in sorted(reasons.items(), key=lambda kv: -kv[1])],
            # a "mungkin" is counted as a no, the same way a polite maybe is a no
            "would_return": ret, "return_rate": round(ret["ya"] / float(n), 3),
            "what_brings_back": [{"answer": k, "count": v} for k, v in sorted(back.items(), key=lambda kv: -kv[1])][:8]}


def data_md(rv, sv, lv=None):
    L = ["# What customers say: the data", ""]
    if lv:
        L += ["## Ratings, as each page shows them", "", "%.1f across %d reviews, weighted by the number of reviews." % (
            lv["rating_avg"], lv["reviews"]), "", "| source | rating | reviews | |", "| --- | ---: | ---: | --- |"]
        L += ["| %s | %.1f | %s | %s |" % (l["source"], l["rating"], "{:,}".format(l["reviews"]).replace(",", "."), l["url"])
              for l in lv["listings"]]
        L.append("")
    if rv:
        L += ["## Reviews read", "", "%d reviews read, worst first, so their average (%.1f) is not the rating;"
              " %.0f%% of those read are 3 stars or fewer." % (rv["reviews"], rv["sample_rating"], rv["low_star_share"] * 100), "",
            "| source | reviews read | their average |", "| --- | ---: | ---: |"]
        L += ["| %s | %d | %.1f |" % (s["source"], s["reviews"], s["rating"]) for s in rv["sources"]]
        L += ["", "| complaint | reviews | of them 1-3 stars | average stars | |", "| --- | ---: | ---: | ---: | --- |"]
        L += ["| %s | %d | %d | %.1f | %s |" % (t["theme"], t["count"], t["low"], t["avg_stars"], "thin" if t["thin"] else "")
              for t in rv["complaints"]]
        L.append("")
        for t in rv["complaints"][:5]:
            for q in t["quotes"]:
                L.append("- **%s**, %g stars, %s: \"%s\" (%s)" % (t["theme"], q["stars"], q["source"], q["quote"], q["url"]))
        if rv["praise"]:
            L += ["", "Praise: %d reviews, average %.1f stars." % (rv["praise"]["count"], rv["praise"]["avg_stars"])]
            for q in rv["praise"]["quotes"]:
                L.append("- \"%s\" (%s)" % (q["quote"], q["url"]))
        L.append("")
    if sv:
        w = sv["would_return"]
        L += ["## Customers who stopped buying", "",
              "%d asked. Would come back: %d ya, %d mungkin, %d tidak. Counted as coming back: %.0f%% (a mungkin is a no)." % (
                  sv["answers"], w["ya"], w["mungkin"], w["tidak"], sv["return_rate"] * 100), "",
              "| why they stopped | answers | share | |", "| --- | ---: | ---: | --- |"]
        L += ["| %s | %d | %.0f%% | %s |" % (r["reason"], r["count"], r["share"] * 100, "thin" if r["thin"] else "") for r in sv["reasons"]]
        if sv["what_brings_back"]:
            L += ["", "What would bring them back:"] + ["- %s (%d)" % (b["answer"], b["count"]) for b in sv["what_brings_back"]]
        L.append("")
    return "\n".join(L) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--listings")
    ap.add_argument("--reviews")
    ap.add_argument("--survey")
    ap.add_argument("--out", default="checker")
    a = ap.parse_args(argv)
    if not (a.listings or a.reviews or a.survey):
        print("error: give --listings, --reviews or --survey", file=sys.stderr)
        return 2
    try:
        lv = tally_listings(_rows(a.listings, LISTING_COLS), a.listings) if a.listings else None
        rv = tally_reviews(_rows(a.reviews, REVIEW_COLS), a.reviews) if a.reviews else None
        sv = tally_survey(_rows(a.survey, SURVEY_COLS), a.survey) if a.survey else None
    except FileNotFoundError as e:
        print("error: %s not found" % e.filename, file=sys.stderr)
        return 2
    except DataError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    out = {}
    if lv:
        out.update({"rating_avg": lv["rating_avg"], "reviews": lv["reviews"], "listings": lv["listings"]})
    if rv:
        out["review_tally"] = rv
    if sv:
        out["survey"] = sv
    os.makedirs(a.out, exist_ok=True)
    with open(os.path.join(a.out, "customers.json"), "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    with open(os.path.join(a.out, "customers-data.md"), "w", encoding="utf-8") as fh:
        fh.write(data_md(rv, sv, lv))
    parts = []
    if lv:
        parts.append("rating %.1f across %d reviews" % (lv["rating_avg"], lv["reviews"]))
    if rv:
        parts.append("%d reviews read, top complaint %s" % (rv["reviews"],
                                                                  rv["complaints"][0]["theme"] if rv["complaints"] else "none"))
    if sv:
        parts.append("%d lapsed customers, top reason %s" % (sv["answers"], sv["reasons"][0]["reason"]))
    print("%s. Wrote %s and customers-data.md" % ("; ".join(parts), os.path.join(a.out, "customers.json")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
