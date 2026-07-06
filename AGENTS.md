# Bookmarks Sync

Version: V1.0
Author: Rames

---

# Project Philosophy

Bookmarks Sync is a lightweight, local-first capture engine.

Its purpose is to synchronise bookmarks from a designated browser bookmark folder into an Obsidian Inbox as Markdown notes.

Bookmarks Sync should never try to think for the user.

It should only capture information safely and reliably.

The software should be:

- Local-first
- Fast
- Reliable
- Modular
- Easy to understand
- Easy to maintain
- Extensible

This project deliberately avoids unnecessary complexity.

If a feature is not required for V1, it should not be implemented.

---

# High-Level Workflow

Browser Bookmark

↓

Bookmarks Sync

↓

Capture Record (Markdown)

↓

Obsidian Inbox

↓

User processes note manually

Bookmarks Sync never categorises, summarises or edits notes.

It only captures.

---

# V1 Goal

When I bookmark a webpage into the Chrome bookmark folder

📥 Obsidian Inbox

Bookmarks Sync should automatically create a Markdown note inside

00 Inbox

within at most one hour.

When Windows starts it should perform one immediate sync.

No user interaction should be required.

---

# Functional Requirements

## Browser

Supported browser:

Google Chrome only.

Future browsers:

- Firefox
- Edge
- Brave

Do not implement future browser support.

---

## Bookmark Folder

Only read bookmarks inside

📥 Obsidian Inbox

Ignore every other bookmark.

---

## Sync Schedule

On Windows startup

↓

Immediate sync

↓

Remain running

↓

Wait 60 minutes

↓

Sync

↓

Repeat forever

The interval must be configurable.

---

## Duplicate Prevention

A bookmark must only ever be imported once.

Maintain a state file.

Example:

state/imported.json

Store enough information to uniquely identify imported bookmarks.

If bookmark already imported

↓

Skip.

---

## Markdown Output

Each bookmark becomes one Markdown file.

Example filename:

BG 2.13 - Soul.md

---

Frontmatter:

```yaml
---
type: inbox
source: chrome-bookmark
processed: false

url: https://...

created: 2026-07-06T12:30:00
---
```

Body:

```markdown
# BG 2.13 - Soul

## URL

https://...

## Notes

```

No additional content.

---

## Configuration

Use config.json.

Example:

```json
{
  "vault_path": "C:/Users/Administrator/OneDrive/Documents/Obsidian Vault",
  "inbox_folder": "00 Inbox",
  "bookmark_folder": "📥 Obsidian Inbox",
  "poll_interval_minutes": 60
}
```

Never hard-code paths.

---

## Logging

Create logs.

Log:

- startup
- shutdown
- sync started
- sync completed
- imported bookmark
- skipped duplicate
- errors

Logs should never crash the application.

---

## Error Handling

The application must continue running if:

- Chrome bookmarks file missing
- Obsidian vault missing
- bookmark folder missing
- malformed bookmark
- invalid filename
- permission error

Errors should be logged.

---

## Windows Startup

The application should automatically launch when Windows starts.

This should be configurable.

---

# Code Standards

Python 3.14

Use:

- type hints
- docstrings
- logging
- pathlib
- dataclasses where appropriate

Prefer:

simple functions

over

large classes.

Avoid global variables.

Avoid overengineering.

---

# Dependencies

Prefer the Python standard library.

Only add third-party packages when they provide significant benefit.

Every dependency should have a clear justification.

---

# Folder Structure

bookmarks-sync/

README.md

PROMPT.md

requirements.txt

config.example.json

docs/

src/

tests/

---

Inside src:

bookmarks_sync/

main.py

config.py

scheduler.py

chrome_reader.py

markdown_writer.py

state_manager.py

logger.py

utils.py

---

# Testing

Every module should be independently testable.

Avoid tightly coupled code.

---

# Design Principles

Bookmarks Sync should be deterministic.

Given the same bookmarks,

it should always produce the same output.

The application should never modify existing Markdown notes.

It only creates new ones.

---

# Things NOT to Implement

Do NOT implement:

AI

OCR

PDF reading

Semantic search

SQLite

Browser extension

GUI

System tray

Notifications

Automatic categorisation

Automatic tagging

Automatic summaries

Obsidian plugins

Cloud sync

Databases

These belong to future versions.

---

# Future Roadmap

## V2

Support Firefox

Support Edge

Support Brave

Browser extension

---

## V3

PDF Capture

Image Capture

Voice Capture

---

## V4

Generic Capture Engine

Multiple exporters

Markdown

JSON

SQLite

---

## V5

Integration with VerseLearn

Optional only.

VerseLearn must remain an independent application.

---

## V6

JARVIS ecosystem

Semantic search

Research assistant

Knowledge graph

Never implement these in V1.

---

# Success Criteria

A user creates a bookmark

↓

inside

📥 Obsidian Inbox

↓

Bookmarks Sync automatically imports it

↓

Markdown note appears inside

00 Inbox

↓

No duplicates

↓

No user intervention required

↓

Application continues running indefinitely.
