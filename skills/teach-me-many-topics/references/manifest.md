# Manifest schema

`scripts/build_index.py` reads this file and writes the index page.
Keep the manifest beside the index output. Edit it and rebuild when the set changes.

```json
{
  "key": "doordash-loop",
  "title": "The Reading Path",
  "eyebrow": "Senior loop preparation",
  "lede": "One or two sentences. Say what the set covers and how to mark a page.",
  "footnote": "One line under the list. Note where progress is saved.",
  "groups": [
    {
      "name": "Local state",
      "note": "Why this group sits here, and what it assumes.",
      "core": true,
      "items": [
        {
          "slug": "btree",
          "title": "B-Tree or LSM",
          "desc": "One line. What the page teaches.",
          "url": "btree.html",
          "tag": "earlier",
          "summary": "Two or three sentences. The page's foundation idea and why it matters.",
          "resources": [
            {"title": "Designing Data-Intensive Applications, ch. 4", "url": "https://dataintensive.net/"}
          ]
        }
      ]
    }
  ]
}
```

## Fields

| Field | Required | Meaning |
|---|---|---|
| `key` | yes | Lowercase slug. Prefixes this set's browser-storage keys, including each page's quiz key `<key>/<slug>`. |
| `title` | yes | The page name. Two to four words. |
| `eyebrow` | no | Small label above the title. |
| `lede` | no | Intro sentence under the title. |
| `footnote` | no | Line under the list. |
| `summary` | no | Two to four sentences under the title that say what the set covers and how to use it. |
| `resources` | no | Up to five `{title, url, note}` readings for the whole set, shown under the summary. `note` is one short clause. |
| `groups[].name` | yes | The group heading. |
| `groups[].note` | no | One or two sentences on the group's place in the order. |
| `groups[].core` | no | `true` puts the group in the Core filter. |
| `items[].slug` | yes | Lowercase slug, unique across the whole manifest. |
| `items[].title` | yes | The page title, as published. |
| `items[].desc` | no | One line under the title. |
| `items[].url` | yes | The relative path `<slug>.html` beside the index. Quiz scores reach the index only from pages on its origin. |
| `items[].tag` | no | Short label on the right, such as `earlier`. |
| `items[].summary` | no | Two or three sentences shown under the title on the index. |
| `items[].resources` | no | Up to three `{title, url}` outside readings, each with an `https://` url. |

## Rules the script enforces

- Every slug matches `[a-z0-9][a-z0-9-]*` and appears once.
- Every item carries a relative `.html` path or an `https://` URL, so build each page first.
- Every resource carries a title and an `https://` URL.
- Every group holds at least one item.

A slug keys one item's saved status and quiz score. Renaming a slug or the key resets that progress.
Keep slugs stable when you rebuild.
