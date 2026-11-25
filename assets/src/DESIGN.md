# Profile README design

One system for the whole page: two night-scene banners (already built) and a family of
generated cards that share their palette, fonts and spacing. Every card is an SVG written by
`build.py`; live numbers come from `data.json`, which `fetch.py` refreshes from the GitHub API.

## Audience and job

A recruiter or engineer who gives the page 20 seconds. The page has to show, with proof they
can click, that this person ships and reviews real work. The memorable element is the vitals
card. Everything else stays quiet.

## Page order

The README is seven category cards, each a paragraph of stacked image segments (no markdown
headings, no code block, no other text). Order:

1. Card 1: `hero`
2. Card 2: `vitals`: the last 53 weeks of contributions drawn as a monitor trace, with three readouts
3. Card 3: `git-hospital` banner (without its tool strip: the rows below replace it), then
   four tool rows, each linking to its repository
4. Card 4: `head-open-source`: title "Open source" and, right-aligned in muted data type, "each row opens
   my pull requests there"; links to the merged pull request search
   then one row per upstream project, each linking to my pull requests there
5. Card 5: `work`: title "Work", then its rows
6. Card 6: `team`: title "Team products" and, in muted sentence type, "private repos, happy to walk
   through the code", then its rows
7. Card 7: `stack`: title "Stack", five rows (label in muted data type, values
   in sentence type), a hairline, then three muted facts: B.Eng. Information Technology, WSB
   Merito Wrocław; Oracle Cloud Infrastructure 2025 Foundations Associate; Turkish, English
   (C1+), Polish (A2-B1)

No content is added that the README did not already state, except numbers read from the public
GitHub API.

## Tokens

Fonts (embedded as subsets per file): Fraunces 600 for names, titles and numerals, Inter 400
for sentences, JetBrains Mono 500 only for data: counts, dates, repository paths.

| Token | Value |
| --- | --- |
| card background | `#0c0a09` (the Git Hospital band keeps its `#171310` scene) |
| raised surface | `#171310` |
| border | `#3a2f28` |
| ink strong | `#f4ece2` |
| ink body | `#d1c3b4` |
| ink muted | `#968779` |
| vital (trace, accents) | `#c7331e` |
| in review | `#d9a441` |
| merged | `#7fb069` |

One palette, always: the night palette of the banners. There is no light theme and no
`prefers-color-scheme` rule. Colors are CSS custom properties on the root `svg`.

Scale: desktop cards use a 1200-unit wide viewBox, like the banners. Phone cards use a
440-unit wide viewBox with the same type sizes: the README column is 308px wide on a 390px
screen, so a 20-unit sentence renders at 14px.

Delivery: `<picture>` chooses the file by width only
(`<source media="(max-width: 600px)" srcset="assets/x-phone.svg">`), and every `<img>` carries
`align="top"`: such images in one paragraph stack with 0px between them on github.com, so each
card is one paragraph with one line per segment, and a blank line between paragraphs gives the
16px gap between cards. Every generated SVG root carries `preserveAspectRatio="none"`: Safari
rounds the image box height, and with the default "meet" the drawing would shrink to fit and
leave a sliver at both sides of short segments, so the border would jog. With "none" the drawing
always fills the box (distortion under 1%).

Category cards: all segments share the background; the first segment of a card has round top
corners (radius 18) and the top border, the last has round bottom corners and the bottom border,
and a single-segment card has all four. The corner cut-outs are transparent, because the cards
sit on GitHub's page background (#0d1117 dark, #ffffff light). A 1-unit border in the border
color runs along the left and right edge of every segment at the same x. Scaled heights are
fractional, so every segment except the last of its card ends with a full-width 1-unit hairline
exactly at its bottom edge to hide any seam; the last segment ends with the card's bottom border
instead. There are no other separators between segments. Hairlines between rows inside work and team are full width too.
Section starts have 44 units of top padding, rows 30.

| Role | Size (units) |
| --- | --- |
| readout numeral | Fraunces 600, 56 |
| row name | Fraunces 600, 28 |
| sentence | Inter 400, 20, line height 30 |
| data | JetBrains Mono 500, 16 |

Side padding 40 units; rows 30 units top and bottom; section titles Fraunces 600, 30.

## Vitals card

The trace is a real chart. X is the 53 weeks ending this week, Y is contributions that week.
Each week is one heartbeat: a short dip, a spike to the week's value, a short undershoot, back
to the baseline; a week with no contributions is flat. Scale: linear from zero up to a ceiling
that is the second-highest week rounded up to the next 50 (a single outlier must not flatten
the rest). A week above the ceiling is drawn to the top edge with a break mark (two short
parallel slashes across the spike) and its real value beside it, without a word. Two faint
dotted reference lines with small data-type labels at the left edge sit at round steps below
the ceiling. The alt text states the ceiling and the clipped value. Month names sit under the
baseline (every second one on phones).

No framed box inside the card: baseline, reference lines and trace are drawn straight on the
card. Faint dot grid, vital-red trace (2 units, round joins) with a soft glow. Motion: the trace draws once left to right in about 2.4
seconds, then a dot at the current week pulses. `prefers-reduced-motion` shows the finished trace.

Size: desktop plot region about 250 units high, card about 360; phone plot about 170.

Readouts, right of the trace on desktop (x 812 to 1160, one line per label) and under it on
phones (rows of equal height: numeral in a 160-unit column, label right of it on at most two
lines):

- `contributions, last 12 months`
- `pull requests merged in public repos` (precisely: in public repositories outside my own
  account; the alt text says so)
- `public pull requests reviewed` (pull requests by others that I reviewed; counted
  by search with `is:public`, so the account's token and the workflow's token agree)

Under the readouts, in data type and never wrapped: `129 active days`, `longest streak 21 days`.
`updated YYYY-MM-DD from the GitHub API` sits bottom left under the month labels on desktop
and on the last line of the card on phones. The date is the day the numbers last changed.

## Rows

One component, three uses. Desktop: name column (x 40 to 330), sentence column (x 350 to 930),
state column right-aligned at 1160. On tool rows the sentence column ends 40 units left of the pill. Phone: name, then sentence at full width, then state.
Sentences wrap by measured glyph advances (fontTools), never by character count.

- Tool row: name, the README's description, status text in an outlined pill.
- Open source row: owner in muted data type above the repository name, star count; the title
  of the latest merged pull request (one line on desktop, at most two on phones, cut with an ellipsis by measurement) and its
  date; right: merged count with a merged-colored dot, and the in-review count with an
  in-review-colored dot when it is not zero.
- Work and team cards: rows inside one card, separated by a border-colored hairline; team
  rows carry their `Built with` list as a data line under the sentence.

## Content

Tools (status text is hand-written, not read from releases):

| Name | Link | Description | Status |
| --- | --- | --- | --- |
| Helmbulance | Git-Hospital/helmbulance | Installs a Helm chart on a throwaway kind cluster and runs day-2 scenarios: upgrades, reinstalls, Secret rotation, network isolation | pre-release |
| MeshMedic | Git-Hospital/meshmedic | Matches Istio's Prometheus telemetry against reviewed failure scenarios and opens a GitOps pull request with the diagnosis, evidence and rollback plan | v1.0.0 |
| boards | Git-Hospital/boards | Benchmark for diagnosis tools: known defects, clean twins and hand-verified values, scored by applying the fix | in development |
| GitHealthCheck | Git-Hospital/githealthcheck | Code health analyzer: tests, history, complexity. Every number is a measurement, or null with a reason | Go rewrite in progress |

Open source rows come from an explicit allowlist in `fetch.py`, in this order. A repository
is never shown because the API returned it; only because it is on the list.

- `nordstjernen-web/nordstjernen-sol-browser`
- `getsentry/relay`
- `istio/istio.io`
- `nordstjernen-web/southstar-browser`
- one static row: `harfbuzz/harfbuzz`, sentence `Reported a text-shaping bug that was fixed the same day`, state `issue #6320`, link https://github.com/harfbuzz/harfbuzz/issues/6320

Work:

| Name | Place | Sentence |
| --- | --- | --- |
| Bluesense | Boston, remote | iOS app in Swift and SwiftUI: session, checkout and cart fixes, release tooling, and GitHub automation for a team of about 30 |
| Nordstjernen | open source | Maintainer of an open-source browser engine in C: 200+ commits, made Google Search and Gmail sign-in work |
| BirthdayMessaging | UK, remote | Security scanning of a production messaging platform with OWASP ZAP, Burp Suite and nmap |

Team products:

| Name | Sentence | Built with |
| --- | --- | --- |
| EmlakPlus | Largest contributor (team of 4) to a CRM for real-estate agencies: listings, clients, map search, scheduled social posts | FastAPI, Next.js, PostgreSQL, Redis, Celery, Terraform |
| data-stock | REST API and admin web of an inventory SaaS that logs stock by barcode and syncs Amazon, Allegro and eBay listings | FastAPI, Alembic, React, Vite, Playwright |
| Vantage | TypeScript API of an Instagram analytics app: Graph API login, ad-supported free tier, Fly.io deploys | Node.js, TypeScript, Docker, Fly.io |

## Decisions on record

- Work and team rows are images, not markdown text. Objection raised in review (2026-11-24):
  image text cannot be searched or selected, a row can carry only one link, and it shrinks
  on phones. Overruled because the HarfBuzz link moved to its own open source row, the phone
  files keep sentences at 14px, the alt text states every fact, and the Stack block stayed
  as searchable text (it has since moved into the card, see below). Revisit if a second link per row is ever needed.
- 2026-11-24, at the owner's request (one card, one design): the light theme is removed and the
  Stack block moved into the card as the last segment. The Safari note about SVG images
  following the OS color scheme is obsolete and deleted. Work and team rows stay images
  (see the objection above), now with in-card titles instead of markdown headings.
- 2026-11-25, at the owner's request: the single card was split into one card per category,
  because the single stack read as an undifferentiated list. Palette, fonts and row design are
  unchanged.

## Data rules

- Only public data. Every search carries `is:public`; the workflow uses the default
  `GITHUB_TOKEN`, which cannot see private repositories anyway.
- A number that cannot be fetched keeps its last value from `data.json`; the build never
  writes a guess or a zero in its place.
- Every image has alt text that states the same facts as the picture.
