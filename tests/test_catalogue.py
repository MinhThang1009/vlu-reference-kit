"""Đối soát khả năng tra cứu tài nguyên trong catalogue offline."""

from html.parser import HTMLParser
from pathlib import Path
import json
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


if __name__ == "__main__":
    unittest.main()
