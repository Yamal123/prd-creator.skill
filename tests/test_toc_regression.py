from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent.parent
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


def assert_contains(pattern: str, message: str, flags: int = 0) -> None:
    if not re.search(pattern, HTML, flags):
        raise AssertionError(message)


assert_contains(
    r"function getScrollOffset\(\)",
    "TOC scroll offset should be calculated from the live sticky navigation height.",
)

assert_contains(
    r"el\.id=`\$\{tabId\}-h-\$\{i\}`",
    "Generated heading ids should be namespaced by tab id to avoid cross-tab anchor collisions.",
)

assert_contains(
    r"tocbot\.init\(\{[\s\S]*headingsOffset:getScrollOffset\(\)[\s\S]*scrollSmoothOffset:-getScrollOffset\(\)",
    "tocbot should use the same dynamic offset for active highlighting and smooth scrolling.",
)

assert_contains(
    r"disableTocScrollSync:true",
    "tocbot built-in scroll sync should be disabled so custom reading-line highlighting is authoritative.",
)

assert_contains(
    r"function updateActiveToc\(\)[\s\S]*readingLine=getScrollOffset\(\)\+90",
    "TOC active state should use a reading line that matches the visible content area.",
)

assert_contains(
    r"localStorage\.getItem\(sk\).*?isPreviewFresh\(\)",
    "Markdown localStorage cache should be bypassable during preview refreshes.",
    re.S,
)

assert_contains(
    r"\.md-toc::after[\s\S]*is-active-link::before",
    "TOC should render a clear reading rail and active marker.",
)

print("TOC regression checks passed")
