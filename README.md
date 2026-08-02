# Site

Static site generator in one Python file. No framework, no JavaScript, no database.

## Setup (once)

1. **Set your domain.** Open `build.py` and edit `CONFIG` at the top —
   `site_url`, `title`, `tagline`, `author`, `description`. The build warns you
   until `site_url` is changed from the placeholder.

2. **Install the one dependency** (already present on this machine):

   ```
   pip install mistune
   ```

## Writing

Put a Markdown file in `content/posts/` (longer pieces), `content/notes/`
(short, rough), or `content/etc/` (films, books, anything that is not work).
Front matter goes at the top between `---` lines:

```markdown
---
title: What I measured
date: 2026-08-01
description: One line. This is what search engines and RSS readers show.
status: budding
---

Body starts here.
```

All keys are optional except that you want `title` and `date`. See
`content/posts/_example.md` for the full reference. Set `draft: true` to keep a
file out of the build.

`status` is optional and can be `seedling`, `budding`, or `evergreen`. It renders
as a labelled box at the top of the page — a fixed place to put uncertainty so
individual sentences do not have to hedge.

`lang` is optional. The site default is `CONFIG["lang"]`; put `lang: ko` on a
Korean entry so the page is not served as English.

## Build

```
python build.py            # writes docs/
python build.py --serve    # writes docs/, then serves http://localhost:8000
```

`docs/` is generated. Never edit it by hand; it is deleted and rebuilt every time.

## Publishing (GitHub Pages)

1. Create a **new public repo** on GitHub. Do not put this inside a repo that
   holds clinical or unpublished research material.
2. Push this directory to it.
3. Repo → Settings → Pages → Source: **Deploy from a branch**, branch `main`,
   folder **`/docs`**.
4. For a custom domain: Settings → Pages → Custom domain. Add a `CNAME` file
   containing your domain to `static/`, so it survives rebuilds.

## Layout

```
build.py              the whole generator, ~200 lines
templates/
  base.html           page shell: head, header, footer
  entry.html          a single post or note
static/style.css      the only stylesheet
content/
  posts/              longer pieces
  notes/              short, rough
  etc/                films, books, not work
docs/                 generated output, served by GitHub Pages
```

Sections are declared in `SECTIONS` in `build.py`. Adding one there creates its
directory listing, its nav link, and its sitemap entry — nothing else to edit.

## Analytics

`CONFIG["analytics"]` is raw HTML injected before `</body>` on every page. Empty
means no third-party script runs on the site at all. Paste a beacon snippet there
to turn measurement on; delete it to turn measurement off. There is no other
place in the build where a third-party script can enter.

## What is already handled

- RSS at `/rss.xml`, linked from `<head>` on every page
- `sitemap.xml` and `robots.txt` for search engines
- `<title>`, `<meta name="description">`, canonical URL, OpenGraph tags
- Dates and word counts on every entry
- Light and dark themes via `prefers-color-scheme`
- Wide tables and long code lines scroll inside their own box, never the page
- `.nojekyll` so GitHub Pages serves the files as-is
