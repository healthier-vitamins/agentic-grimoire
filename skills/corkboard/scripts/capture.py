"""Screenshot one web page as evidence for a corkboard item.

    uv run --with playwright python -I capture.py <url> <out.png> [--selector CSS] [--full]

Loads <url> in Chrome at 1280x900, waits for the network to settle, and saves the viewport (or
the element matching --selector, or the full page with --full). Prints the media.json entry
fields it knows, so the caller only adds key, alt and source.label.
"""

import argparse
import datetime
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

__all__ = ["capture"]


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0]
    )
    parser.add_argument("url")
    parser.add_argument("out", type=Path)
    parser.add_argument(
        "--selector", help="shoot only this element, e.g. a review or a seat map"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="shoot the whole page, not just the viewport",
    )
    args = parser.parse_args()
    title = capture(args.url, args.out, args.selector, args.full)
    entry = {
        "file": args.out.name,
        "kind": "screenshot",
        "source": {"label": title, "url": args.url},
        "captured": datetime.date.today().isoformat(),
    }
    print(json.dumps(entry, ensure_ascii=False, indent=2))


def capture(
    url: str, out: Path, selector: str | None = None, full: bool = False
) -> str:
    """Save the screenshot to out and return the page's title."""
    out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(url, wait_until="networkidle", timeout=45_000)
        if selector:
            page.locator(selector).first.screenshot(path=out)
        else:
            page.screenshot(path=out, full_page=full)
        title = page.title()
        browser.close()
    return title


if __name__ == "__main__":
    main()
