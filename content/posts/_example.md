---
title: Example post
date: 2026-08-01
status: seedling
description: One-line summary used in RSS and search results.
draft: true
---

Delete this file, or set `draft: true` to `false` to publish it.

## Front matter reference

| key | what it does |
|---|---|
| `title` | Page title. Also the `<title>` tag and the RSS item title. |
| `date` | `YYYY-MM-DD`. Falls back to a date prefix on the filename, then to file mtime. |
| `description` | One line. Used for `<meta name="description">` and the RSS description. Matters for search. |
| `status` | Optional: `seedling`, `budding`, or `evergreen`. Omit for no label. |
| `lang` | Optional BCP 47 code, e.g. `ko`. Overrides the site default for this page only. Set it on Korean entries. |
| `slug` | Optional. Overrides the URL, which otherwise comes from the filename. |
| `draft` | `true` keeps the file out of the build. |

## What Markdown gives you

Regular paragraphs, **bold**, *italic*, and `inline code`.

```python
# Fenced code blocks work. Long lines scroll inside the block,
# so the page itself never scrolls sideways.
print("hello")
```

> Block quotes are set off with a rule on the left.

- Bullet lists
- Numbered lists
- Tables, as above

Wide tables scroll inside their own box rather than breaking the layout.
