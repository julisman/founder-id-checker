import json
import os
import shutil
import tempfile
import unittest

from _load import load, example

reviews = load("checker-customers", "reviews")


def write(d, name, text):
    p = os.path.join(d, name)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


class Examples(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_tally_the_examples(self):
        rc = reviews.main(["--listings", example("checker-customers", "listings.example.csv"),
                           "--reviews", example("checker-customers", "reviews.example.csv"),
                           "--survey", example("checker-customers", "survey.example.csv"), "--out", self.d])
        self.assertEqual(rc, 0)
        with open(os.path.join(self.d, "customers.json"), encoding="utf-8") as fh:
            c = json.load(fh)
        # the rating is the listings' own, weighted by their review counts
        self.assertEqual(c["reviews"], 1647)
        self.assertEqual(c["rating_avg"], 4.18)
        tally = c["review_tally"]
        self.assertEqual(tally["reviews"], 12)
        self.assertEqual(tally["sample_rating"], 3.25)  # read worst-first: kept, never used as the rating
        self.assertNotIn("rating_avg", tally)
        self.assertEqual([t["theme"] for t in tally["complaints"][:2]], ["lama", "porsi"])
        self.assertEqual(tally["praise"]["count"], 3)
        s = c["survey"]
        self.assertEqual(s["answers"], 8)
        self.assertEqual(s["would_return"], {"ya": 3, "mungkin": 3, "tidak": 2})
        self.assertEqual(s["return_rate"], 0.375)
        self.assertEqual(s["reasons"][0], {"reason": "porsi", "count": 3, "share": 0.375, "thin": False})
        with open(os.path.join(self.d, "customers-data.md"), encoding="utf-8") as fh:
            md = fh.read()
        self.assertIn("a mungkin is a no", md)
        self.assertIn("https://example.com/review/1", md)

    def test_reviews_alone_give_no_rating(self):
        rc = reviews.main(["--reviews", example("checker-customers", "reviews.example.csv"), "--out", self.d])
        self.assertEqual(rc, 0)
        with open(os.path.join(self.d, "customers.json"), encoding="utf-8") as fh:
            self.assertNotIn("rating_avg", json.load(fh))

    def test_listing_counts_with_thousand_dots(self):
        p = write(self.d, "l.csv", "source,rating,review_count,url\nGoFood,4.3,1.250,https://e.x\n")
        self.assertEqual(reviews.tally_listings(reviews._rows(p, reviews.LISTING_COLS), p)["reviews"], 1250)

    def test_every_review_needs_a_link(self):
        p = write(self.d, "r.csv", "source,date,stars,theme,quote,url\nGoogle Maps,2026-11-01,2,lama,lama sekali,\n")
        with self.assertRaisesRegex(reviews.DataError, "link"):
            reviews.tally_reviews(reviews._rows(p, reviews.REVIEW_COLS), p)

    def test_stars_and_columns(self):
        p = write(self.d, "r.csv", "source,date,stars,theme,quote,url\nGoFood,2026-11-01,7,lama,x,https://e.x\n")
        with self.assertRaisesRegex(reviews.DataError, "1 to 5"):
            reviews.tally_reviews(reviews._rows(p, reviews.REVIEW_COLS), p)
        p = write(self.d, "s.csv", "date,reason\n2026-11-01,porsi\n")
        with self.assertRaisesRegex(reviews.DataError, "missing the column"):
            reviews._rows(p, reviews.SURVEY_COLS)

    def test_would_return_must_be_clear(self):
        p = write(self.d, "s.csv", "date,last_bought,reason,would_return,what_brings_back\n2026-11-01,2026-09,porsi,entahlah,\n")
        with self.assertRaisesRegex(reviews.DataError, "ya, mungkin or tidak"):
            reviews.tally_survey(reviews._rows(p, reviews.SURVEY_COLS), p)


if __name__ == "__main__":
    unittest.main()
