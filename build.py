#!/usr/bin/env python3
"""
Static site generator.

Reads Markdown from content/, writes HTML to docs/.
No framework. Standard library + mistune (Markdown parser).

Usage:
    python build.py            build the site into docs/
    python build.py --serve    build, then serve docs/ at http://localhost:8000

Everything is configured in CONFIG below.
"""

from __future__ import annotations

import html
import re
import shutil
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from string import Template
from urllib.parse import urlsplit

import mistune

# --------------------------------------------------------------------------
# CONFIG — edit these
# --------------------------------------------------------------------------

CONFIG = {
    # No trailing slash. Used for RSS, sitemap, and canonical URLs.
    "site_url": "https://yusin.kim",
    "title": "Yusin Kim",
    "tagline": (
        "A pediatric allergist, some coding agents, "
        "and an inappropriate amount of measurement."
    ),
    "author": "Yusin Kim",
    # Footer identity. One line per element; leave the tuple empty to omit the
    # block entirely. `orcid` is the bare identifier, not a URL.
    "affiliation": (
        "Division of Allergy and Pulmonology, Department of Pediatrics",
        "Ajou University School of Medicine, Suwon, Republic of Korea",
    ),
    "orcid": "0000-0002-0303-8907",
    # Shown in the RSS feed and the homepage <meta name="description">.
    "description": (
        "Measurements and notes on AI agents, tooling, and research workflow, "
        "written by a physician-researcher."
    ),
    # Default page language. Any entry can override it with `lang:` in front
    # matter — a Korean film note should not be served as lang="en".
    "lang": "en",
    # Raw HTML injected before </body> on every page. Analytics beacon goes
    # here. Empty string means no third-party script runs on the site at all.
    "analytics": (
        '<script data-goatcounter="https://leucine.goatcounter.com/count"\n'
        '        async src="//gc.zgo.at/count.js"></script>'
    ),
}

# Three layers. Cheap notes support expensive posts — this is what keeps the
# site alive when clinical work eats the week. Etc. keeps everything else off
# the front of the other two without hiding it.
SECTIONS = {
    "posts": {
        "title": "Writing",
        "blurb": "Longer pieces. Usually something I measured.",
    },
    "notes": {
        "title": "Notes",
        "blurb": "Short, rougher, often unfinished. Things I am still working out.",
    },
    "etc": {
        "title": "Etc.",
        "blurb": "Films, books, and whatever else. Not work.",
    },
}

# Optional epistemic label, shown on the page when set in front matter.
# Borrowed from Maggie Appleton — a formal place to put uncertainty, so that
# individual sentences do not have to carry it.
STATUS_LABELS = {
    "seedling": "Seedling — early, likely wrong in places.",
    "budding": "Budding — the shape is right, details may move.",
    "evergreen": "Evergreen — I stand behind this.",
}

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUT = ROOT / "docs"


# --------------------------------------------------------------------------
# Front matter
# --------------------------------------------------------------------------

def parse_front_matter(raw: str) -> tuple[dict, str]:
    """Split a `--- key: value --- body` file into (metadata, body).

    Deliberately not YAML. Keys are `key: value`, one per line. That is all
    this site needs, and it means one less dependency.
    """
    if not raw.startswith("---"):
        return {}, raw

    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw

    meta = {}
    for line in parts[1].strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip().lower()] = value.strip().strip('"').strip("'")

    return meta, parts[2].lstrip("\n")


# --------------------------------------------------------------------------
# Page model
# --------------------------------------------------------------------------

class Page:
    def __init__(self, path: Path, section: str):
        raw = path.read_text(encoding="utf-8")
        meta, body = parse_front_matter(raw)

        self.source = path
        self.section = section
        self.meta = meta
        self.body_md = body

        self.title = meta.get("title") or path.stem.replace("-", " ")
        self.description = meta.get("description", "")
        self.status = meta.get("status", "").lower()
        self.draft = meta.get("draft", "").lower() in ("true", "yes", "1")
        self.lang = meta.get("lang") or CONFIG["lang"]

        self.date = self._parse_date(meta.get("date"), path)
        self.slug = meta.get("slug") or self._slug_from(path)
        self.url = f"/{section}/{self.slug}/"

        self.html = mistune.html(body)
        self.words = len(re.findall(r"\b[\w'-]+\b", body))

    @staticmethod
    def _parse_date(value: str | None, path: Path) -> datetime:
        # Front matter wins; otherwise try a YYYY-MM-DD prefix on the filename.
        candidates = [value] if value else []
        m = re.match(r"(\d{4}-\d{2}-\d{2})", path.stem)
        if m:
            candidates.append(m.group(1))
        for candidate in candidates:
            try:
                return datetime.strptime(candidate[:10], "%Y-%m-%d").replace(
                    tzinfo=timezone.utc
                )
            except (ValueError, TypeError):
                continue
        # No date anywhere. Fall back to file mtime rather than omitting it:
        # a post without a visible date is genuinely hard to cite later.
        return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)

    @staticmethod
    def _slug_from(path: Path) -> str:
        stem = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", path.stem)
        return re.sub(r"[^a-z0-9-]+", "-", stem.lower()).strip("-")

    @property
    def iso_date(self) -> str:
        return self.date.strftime("%Y-%m-%d")

    @property
    def full_url(self) -> str:
        return CONFIG["site_url"].rstrip("/") + self.url


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------

def load_template(name: str) -> Template:
    return Template((TEMPLATES / name).read_text(encoding="utf-8"))


def render_nav() -> str:
    """Nav comes from SECTIONS so that adding a section touches one file."""
    links = [
        f'    <a href="/{s}/">{html.escape(info["title"])}</a>'
        for s, info in SECTIONS.items()
    ]
    links.append('    <a href="/rss.xml">RSS</a>')
    return "\n".join(links)


def render_identity() -> str:
    """Author, affiliation, ORCID. Each element is omitted when unset.

    This is the path from the writing back to the person. A site whose output
    travels further than its author is a known failure mode.
    """
    lines = [f'<span class="identity-name">{html.escape(CONFIG["author"])}</span>']
    lines += [html.escape(line) for line in CONFIG.get("affiliation", ())]
    orcid = CONFIG.get("orcid", "")
    if orcid:
        lines.append(
            f'<a href="https://orcid.org/{html.escape(orcid)}">ORCID {html.escape(orcid)}</a>'
        )
    return '<p class="identity">' + "<br>\n  ".join(lines) + "</p>"


def render_page(
    inner: str, *, title: str, description: str, url_path: str, lang: str | None = None
) -> str:
    base = load_template("base.html")
    site_title = CONFIG["title"]
    full_title = title if title == site_title else f"{title} — {site_title}"
    return base.substitute(
        lang=lang or CONFIG["lang"],
        title=html.escape(full_title),
        description=html.escape(description or CONFIG["description"]),
        canonical=CONFIG["site_url"].rstrip("/") + url_path,
        site_title=html.escape(site_title),
        nav=render_nav(),
        identity=render_identity(),
        content=inner,
        year=datetime.now().year,
        author=html.escape(CONFIG["author"]),
        # Substituted values are not rescanned, so a `$` inside the snippet is safe.
        analytics=CONFIG.get("analytics", ""),
    )


def render_entry(page: Page) -> str:
    tpl = load_template("entry.html")
    status_html = ""
    if page.status in STATUS_LABELS:
        status_html = (
            f'<p class="status status-{page.status}">'
            f"{html.escape(STATUS_LABELS[page.status])}</p>"
        )
    return tpl.substitute(
        title=html.escape(page.title),
        iso_date=page.iso_date,
        words=f"{page.words:,}",
        status=status_html,
        content=page.html,
    )


def render_list(section: str, pages: list[Page]) -> str:
    info = SECTIONS[section]
    items = "\n".join(
        f'      <li><time datetime="{p.iso_date}">{p.iso_date}</time>'
        f'<a href="{p.url}">{html.escape(p.title)}</a></li>'
        for p in pages
    )
    return (
        f"<h1>{html.escape(info['title'])}</h1>\n"
        f"<p class=\"blurb\">{html.escape(info['blurb'])}</p>\n"
        f'<ul class="entry-list">\n{items}\n</ul>'
    )


def render_home(by_section: dict[str, list[Page]]) -> str:
    blocks = [
        f"<h1>{html.escape(CONFIG['title'])}</h1>",
        f"<p class=\"tagline\">{html.escape(CONFIG['tagline'])}</p>",
    ]
    for section, pages in by_section.items():
        if not pages:
            continue
        info = SECTIONS[section]
        items = "\n".join(
            f'    <li><time datetime="{p.iso_date}">{p.iso_date}</time>'
            f'<a href="{p.url}">{html.escape(p.title)}</a></li>'
            for p in pages[:10]
        )
        blocks.append(
            f"<h2><a href=\"/{section}/\">{html.escape(info['title'])}</a></h2>\n"
            f'<ul class="entry-list">\n{items}\n</ul>'
        )
    return "\n".join(blocks)


# --------------------------------------------------------------------------
# Feeds and search-engine files
# --------------------------------------------------------------------------

def render_rss(pages: list[Page]) -> str:
    site = CONFIG["site_url"].rstrip("/")
    now = format_datetime(datetime.now(timezone.utc))
    items = []
    for p in pages[:30]:
        items.append(
            "    <item>\n"
            f"      <title>{html.escape(p.title)}</title>\n"
            f"      <link>{p.full_url}</link>\n"
            f'      <guid isPermaLink="true">{p.full_url}</guid>\n'
            f"      <pubDate>{format_datetime(p.date)}</pubDate>\n"
            f"      <description>{html.escape(p.description or p.title)}</description>\n"
            "    </item>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        f"    <title>{html.escape(CONFIG['title'])}</title>\n"
        f"    <link>{site}/</link>\n"
        f"    <description>{html.escape(CONFIG['description'])}</description>\n"
        f"    <language>{CONFIG['lang']}</language>\n"
        f"    <lastBuildDate>{now}</lastBuildDate>\n"
        f'    <atom:link href="{site}/rss.xml" rel="self" type="application/rss+xml"/>\n'
        + "\n".join(items)
        + "\n  </channel>\n</rss>\n"
    )


def render_sitemap(pages: list[Page]) -> str:
    site = CONFIG["site_url"].rstrip("/")
    urls = [f"  <url><loc>{site}/</loc></url>"]
    urls += [f"  <url><loc>{site}/{s}/</loc></url>" for s in SECTIONS]
    urls += [
        f"  <url><loc>{p.full_url}</loc><lastmod>{p.iso_date}</lastmod></url>"
        for p in pages
    ]
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


def render_robots() -> str:
    site = CONFIG["site_url"].rstrip("/")
    return f"User-agent: *\nAllow: /\n\nSitemap: {site}/sitemap.xml\n"


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build() -> None:
    if CONFIG["site_url"] == "https://example.com":
        print("!  CONFIG['site_url'] is still the placeholder.")
        print("!  RSS and sitemap links will be wrong until you set it.\n")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    by_section: dict[str, list[Page]] = {}
    drafts = 0

    for section in SECTIONS:
        pages = []
        src = CONTENT / section
        for path in sorted(src.glob("*.md")) if src.exists() else []:
            page = Page(path, section)
            if page.draft:
                drafts += 1
                continue
            pages.append(page)
        pages.sort(key=lambda p: p.date, reverse=True)
        by_section[section] = pages

        for page in pages:
            write(
                OUT / section / page.slug / "index.html",
                render_page(
                    render_entry(page),
                    title=page.title,
                    description=page.description,
                    url_path=page.url,
                    lang=page.lang,
                ),
            )

        write(
            OUT / section / "index.html",
            render_page(
                render_list(section, pages),
                title=SECTIONS[section]["title"],
                description=SECTIONS[section]["blurb"],
                url_path=f"/{section}/",
            ),
        )

    write(
        OUT / "index.html",
        render_page(
            render_home(by_section),
            title=CONFIG["title"],
            description=CONFIG["description"],
            url_path="/",
        ),
    )

    everything = sorted(
        (p for pages in by_section.values() for p in pages),
        key=lambda p: p.date,
        reverse=True,
    )
    write(OUT / "rss.xml", render_rss(everything))
    write(OUT / "sitemap.xml", render_sitemap(everything))
    write(OUT / "robots.txt", render_robots())

    # GitHub Pages: stop Jekyll from touching the output.
    write(OUT / ".nojekyll", "")

    # GitHub Pages reads CNAME from the root of the published directory, not
    # from static/. Generate it from site_url so the two can never disagree.
    #
    # Setting a custom domain in the Pages UI or API makes GitHub commit this
    # same file itself, so the two writers must agree byte for byte or every
    # domain change collides with the next build. GitHub writes the bare host
    # with no trailing newline; write_text would add a CRLF on Windows.
    host = urlsplit(CONFIG["site_url"]).netloc
    if host:
        (OUT / "CNAME").write_text(host, encoding="utf-8", newline="")

    if STATIC.exists():
        shutil.copytree(STATIC, OUT / "static", dirs_exist_ok=True)

    counts = ", ".join(f"{len(v)} {k}" for k, v in by_section.items())
    print(f"built {counts} -> {OUT.relative_to(ROOT)}/")
    if drafts:
        print(f"       ({drafts} draft{'s' if drafts != 1 else ''} skipped)")


def serve() -> None:
    import http.server
    import socketserver
    import functools

    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(OUT)
    )
    with socketserver.TCPServer(("", 8000), handler) as httpd:
        print("serving http://localhost:8000  (ctrl-c to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        serve()
