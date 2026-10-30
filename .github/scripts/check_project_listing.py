"""Check the built projects listing, including the cross-year MOSAIC regression."""

from html.parser import HTMLParser
from pathlib import Path
import sys


class ProjectListing(HTMLParser):
    def __init__(self):
        super().__init__()
        self.divs = []
        self.grids = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div":
            classes = attrs.get("class", "").split()
            grid = self.divs[-1] if self.divs else None
            if "entries-grid" in classes:
                grid = {"cards": 0, "links": []}
                self.grids.append(grid)
            self.divs.append(grid)
            if grid is not None and "grid__item" in classes:
                grid["cards"] += 1
        elif tag == "a" and self.divs and self.divs[-1] is not None:
            self.divs[-1]["links"].append(attrs.get("href", ""))

    def handle_endtag(self, tag):
        if tag == "div" and self.divs:
            self.divs.pop()


def check(html):
    listing = ProjectListing()
    listing.feed(html)
    assert len(listing.grids) == 1, "Projects must appear in one continuous grid"
    grid = listing.grids[0]
    assert grid["cards"] > 1, "MOSAIC must share its grid with other projects"
    assert any(link.rstrip("/").endswith("/projects/mosaic") for link in grid["links"]), (
        "MOSAIC is missing from the project grid"
    )
    return grid["cards"]


if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "_site/projects/index.html")
    count = check(path.read_text())
    print(f"PASS: MOSAIC shares one grid with all {count} projects.")
