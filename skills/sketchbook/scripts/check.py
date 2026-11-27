"""Render a built board and look for breakage.

    uv run --with playwright python -I check.py <plan-dir>

Opens <plan-dir>/board.html in Chrome at desktop width (light) and phone width (dark). For each it
shoots every board the plan was built with, the first item's popup, and that item's full page into <plan-dir>/check/,
and fails on any console error, page error, or sideways scroll. View every shot afterwards: this
script sees errors, not overlap.
"""

import sys
from pathlib import Path
from typing import Literal

from playwright.sync_api import ConsoleMessage, Page, sync_playwright

__all__ = ["check"]

Scheme = Literal["light", "dark"]
VIEWS: list[tuple[str, int, int, Scheme]] = [
    ("desktop-light", 1440, 900, "light"),
    ("phone-dark", 390, 844, "dark"),
]


def main() -> None:
    plan_dir = Path(sys.argv[1]).resolve()
    problems = check(plan_dir)
    for shot in sorted((plan_dir / "check").glob("*.png")):
        print(shot)
    if problems:
        print("Problems:", *problems, sep="\n  ", file=sys.stderr)
        sys.exit(1)
    print("No console errors, no page errors, no sideways scroll.")


def check(plan_dir: Path) -> list[str]:
    """Shoot every view into plan_dir/check and return what broke."""
    out = plan_dir / "check"
    out.mkdir(exist_ok=True)
    url = (plan_dir / "board.html").as_uri()
    problems: list[str] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome")
        for name, width, height, scheme in VIEWS:
            page = browser.new_page(
                viewport={"width": width, "height": height}, color_scheme=scheme
            )
            errors = _collect_errors(page)
            problems += _shoot_views(page, url, out, name)
            problems += [f"{name}: {e}" for e in errors]
            page.close()
        browser.close()
    return problems


def _shoot_views(page: Page, url: str, out: Path, name: str) -> list[str]:
    problems = []
    page.goto(url)
    boards: list[str] = page.evaluate("BOARDS")
    for board in boards:
        page.goto(f"{url}#{board}")
        page.wait_for_timeout(500)
        problems += _overflow(page, f"{name} {board}")
        page.screenshot(path=out / f"{name}-{board}.png")
    page.goto(f"{url}#{boards[0]}")
    page.wait_for_timeout(400)
    card = page.locator(".cv-world :is(div, li)[data-id]").first
    summary = page.locator(
        ".cv[data-zoom=far] .node:has(:is(div, li)[data-id]):has([data-focus])"
    ).first
    if summary.count():
        node = page.locator(f'[data-node="{summary.get_attribute("data-node")}"]')
        node.locator("[data-focus]").first.click()
        page.wait_for_timeout(300)
        card = node.locator(":is(div, li)[data-id]").first
    item_id = card.get_attribute("data-id")
    card.click()
    page.wait_for_selector(".pm")
    page.screenshot(path=out / f"{name}-popup.png")
    page.goto(f"{url}#{boards[0]}-item-{item_id}")
    page.wait_for_selector(".pfull")
    problems += _overflow(page, f"{name} full page")
    page.screenshot(path=out / f"{name}-page.png", full_page=True)
    return problems


def _collect_errors(page: Page) -> list[str]:
    """A list that fills with the page's console errors and uncaught exceptions as they happen."""
    errors: list[str] = []

    def on_console(message: ConsoleMessage) -> None:
        if message.type == "error":
            errors.append(f"console: {message.text}")

    page.on("console", on_console)
    page.on("pageerror", lambda error: errors.append(f"page error: {error}"))
    return errors


def _overflow(page: Page, where: str) -> list[str]:
    wide = page.evaluate("document.documentElement.scrollWidth - innerWidth")
    return [f"{where}: page scrolls sideways by {wide}px"] if wide > 0 else []


if __name__ == "__main__":
    main()
