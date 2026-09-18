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
          "url": "https://claude.ai/artifact/A8814auqKEss6e6k6kidr3",
          "tag": "earlier"
        }
      ]
    }
  ]
}
```

## Fields

| Field | Required | Meaning |
|---|---|---|
| `key` | yes | Lowercase slug. Names the browser-storage fallback for this set. |
| `title` | yes | The page name. Two to four words. |
| `eyebrow` | no | Small label above the title. |
| `lede` | no | Intro sentence under the title. |
| `footnote` | no | Line under the list. |
| `groups[].name` | yes | The group heading. |
| `groups[].note` | no | One or two sentences on the group's place in the order. |
| `groups[].core` | no | `true` puts the group in the Core filter. |
| `items[].slug` | yes | Lowercase slug, unique across the whole manifest. |
| `items[].title` | yes | The page title, as published. |
| `items[].desc` | no | One line under the title. |
| `items[].url` | yes | An `https://` URL for a published page, or a relative `.html` path beside the index for a local set. |
| `items[].tag` | no | Short label on the right, such as `earlier`. |

## Rules the script enforces

- Every slug matches `[a-z0-9][a-z0-9-]*` and appears once.
- Every item carries an `https://` URL or a relative `.html` path, so build or publish each page first.
- Every group holds at least one item.

A slug keys one item's saved status. Renaming a slug resets that item's progress.
Keep slugs stable when you rebuild.
