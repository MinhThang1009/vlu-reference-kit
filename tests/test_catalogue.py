"""Đối soát khả năng tra cứu tài nguyên trong catalogue offline."""

from html.parser import HTMLParser
from pathlib import Path
import json
import re
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1] / "kit"


class CatalogueCards(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cards = []
        self.current = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "article":
            self.current = {"search": attributes.get("data-search", ""), "links": set()}
        elif tag == "a" and self.current is not None:
            link = urlsplit(attributes.get("href", ""))
            if not link.scheme and not link.netloc and link.path:
                self.current["links"].add(unquote(link.path))

    def handle_endtag(self, tag):
        if tag == "article" and self.current is not None:
            self.cards.append(self.current)
            self.current = None


class CatalogueTests(unittest.TestCase):
    def setUp(self):
        parser = CatalogueCards()
        parser.feed((ROOT / "index.html").read_text(encoding="utf-8"))
        self.cards = parser.cards
        self.ledger = json.loads((ROOT / "data/asset-sources.json").read_text(encoding="utf-8-sig"))

    def test_every_included_asset_has_a_searchable_download_card(self):
        for row in self.ledger:
            if row["included_in_package"]:
                name = row["file"]
                with self.subTest(asset=name):
                    self.assertTrue(any(name in card["links"] and name.lower() in card["search"]
                                        for card in self.cards), "Missing searchable download card")

    def test_withheld_assets_have_no_local_download_links(self):
        linked = set().union(*(card["links"] for card in self.cards))
        for row in self.ledger:
            if not row["included_in_package"]:
                with self.subTest(asset=row["file"]):
                    self.assertNotIn(row["file"], linked)

    def test_current_inventory_summaries_match_the_asset_ledger(self):
        included = sum(row["included_in_package"] is True for row in self.ledger)
        withheld = sum(row["included_in_package"] is False for row in self.ledger)
        cases = (
            (ROOT.parent / "README.md",
             r"Có (\d+) tài nguyên kèm theo và metadata cho (\d+) tài nguyên",
             (included, withheld)),
            (ROOT.parent / "THIRD_PARTY_NOTICES.md",
             r"Gói cộng đồng giữ (\d+) tài nguyên kèm theo và metadata cho (\d+) tài nguyên bị loại",
             (included, withheld)),
            (ROOT / "README.md",
             r"Ledger có (\d+) bản ghi, gồm (\d+) mục kèm file và (\d+) mục chỉ có metadata",
             (len(self.ledger), included, withheld)),
            (ROOT / "PUBLICATION.md",
             r"Sổ nguồn hiện tại có (\d+) bản ghi: (\d+) bản ghi được kèm theo và (\d+) bản ghi bị loại",
             (len(self.ledger), included, withheld)),
        )
        for path, pattern, expected in cases:
            with self.subTest(document=path.relative_to(ROOT.parent).as_posix()):
                summary = re.search(pattern, path.read_text(encoding="utf-8"))
                self.assertIsNotNone(summary, "Current inventory summary is missing")
                self.assertEqual(tuple(map(int, summary.groups())), expected)


if __name__ == "__main__":
    unittest.main()
