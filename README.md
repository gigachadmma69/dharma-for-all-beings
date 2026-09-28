# For All Beings

A portable Buddhist teaching library: exact wording, translator credits, context and primary-source links. Software is MIT-licensed; translations are not. See RIGHTS.md.

## What works

- 32 independently source-checked short passages, with permanent local anchors and a downloadable JSON archive.
- A compassion-first editorial reading order, not an objective measure of spiritual benefit.
- A prepared daily GitHub Actions source-check workflow (not active: current GitHub authorization lacks workflow permission). It reads existing sources, checks exact text and gathers same-source links as research candidates. When installed at .github/workflows/research.yml, it produces a report and a portable website artifact. The template is in automation-templates/research.yml.
- A separate authorized Codex task curates new passages, manages native X scheduling, and republishes the library. It needs the user's computer and account access.

## What is NOT autonomous yet

The website is static; it neither calls an AI model nor posts to X. The source watcher is not a scholar: matching words is insufficient to verify context, authorship, translation rights or helpfulness. Reports never auto-promote candidates. No hosted AI or X credentials have been configured. No independent always-on publisher is running.

## Build and research

Python 3, no additional packages:

```
python3 scripts/build.py
python3 scripts/research.py
python3 -m http.server 8000 --directory dist
```

Publish `dist/` on any static host. The ChatGPT Site is one host, not a dependency of the archive. Keep backups on independent providers and offline. To update, verify a passage in full context; add its exact quote, actual speaker, work, translator, locator, source URL, verification date and context note to archive.json; rebuild and deploy. Never include credentials, private account data or browser sessions.

## Long-term continuity

At one post per 15 minutes: 96 posts/day, 672/week, 35,040/non-leap year. A high frequency consumes a finite verified backlog quickly; it does not prove greater benefit. Native X scheduling currently delivers posts; verify its actual queue rather than inferring coverage from this archive.

For operation without the owner's computer, a custodian must configure and maintain a hosted scheduler, authorized AI research access if wanted, and X user-authorized publishing credentials with a funded budget where needed. Keep a persistent publication ledger, reserve an item before sending, record the returned X post ID, and reconcile uncertain sends before retrying. Never automatically repeat an ambiguous send. Use expiring failure alerts, periodic restore drills, and a documented successor. Do not make the publishing process invent a quotation to fill a slot.

GitHub scheduled workflows can be delayed, and public-repository schedules are disabled after 60 days without activity. Artifact retention is limited. This is a research aid and reproducible archive, not a perpetuity guarantee. See https://docs.github.com/en/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows .

A succession plan requires a real person and ongoing account/service arrangements; none is established by this repository. Do not impersonate the owner or write personal updates on their behalf. The mission is attributed teachings that invite wisdom and compassion, with no promised spiritual outcome.

## Multimedia and distribution

The library includes two excerpts verified against official James Low and Lama Lena transcript sources, links to their full teachings, and an Erik Pema Kunsang interview about Tulku Urgyen (explicitly a recollection, not Tulku Urgyen speaking). See media.json for exact verification levels. Transcript section timestamps are not claimed to be audio-verified sentence timestamps.

The portable RSS feed is dist/feed.xml. Readers can subscribe without X. It updates when the library is rebuilt and republished, not independently every fifteen minutes. Website and repository continuity do not depend on X access; the updating process still depends on local Codex. No account-replacement or ban-evasion automation is configured. If X is suspended, stop X writes, report the state, and maintain the library/feed. Use an appeal or an independently authorized compliant distribution channel; do not create replacement accounts to circumvent enforcement.
