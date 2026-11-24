# Profile README design

One system for the whole page: two night-scene banners (already built) and a family of
generated cards that share their palette, fonts and spacing. Every card is an SVG written by
`build.py`; live numbers come from `data.json`, which `fetch.py` refreshes from the GitHub API.

## Audience and job

A recruiter or engineer who gives the page 20 seconds. The page has to show, with proof they
can click, that this person ships and reviews real work. The memorable element is the vitals
card. Everything else stays quiet.

## Page order

1. `hero` (existing)
2. `vitals`: the last 53 weeks of contributions drawn as a monitor trace, with three readouts
3. `git-hospital` banner (existing, without its four-tool footer strip: the rows below replace it)
4. four tool rows, one image each, each linking to its repository
5. `## Open source`, then one row per upstream project, each linking to my pull requests there
6. `## Work`, then one card
7. `### Team products (private repos, happy to walk through the code)`, then one card
8. `## Stack` stays as the existing text block, and the footer line stays as text

The three markdown tables are removed. No content is added that the README does not already
state, except numbers read from the public GitHub API.

## Tokens

Fonts (already embedded as subsets): Fraunces 600 for names and numerals, Inter 400/500 for
sentences, JetBrains Mono 500 only for data: counts, dates, repository paths.

| Token | Dark (base) | Light (`prefers-color-scheme: light`) |
| --- | --- | --- |
| card background | `#0c0a09` | `#ffffff` |
| raised surface | `#171310` | `#f6f9fc` |
| border | `#3a2f28` | `#d6e0e9` |
| ink strong | `#f4ece2` | `#0f1c2a` |
| ink body | `#d1c3b4` | `#2d3d4e` |
| ink muted | `#968779` | `#5e7082` |
| vital (trace, accents) | `#c7331e` | `#dc383e` |
| in review | `#d9a441` | `#a8720f` |
| merged | `#7fb069` | `#16803f` |

Dark is the night palette of the banners. Light is the palette of kadirhanemrememis.xyz. The
two banners are illustrations and stay dark in both themes. Colors are CSS custom properties
on the root `svg`, overridden inside one media query, so one file serves both themes.

Scale: desktop cards use a 1200-unit wide viewBox, like the banners. Phone cards use a
440-unit wide viewBox with the same type sizes: the README column is 308px wide on a 390px
screen, so a 20-unit sentence renders at 14px.

Delivery: `<picture>` chooses the file by width only
(`<source media="(max-width: 600px)" srcset="assets/x-phone.svg">`), and each SVG switches
theme inside its own `<style>`. Width and color scheme are never combined in one `media`:
GitHub's themed-picture script rewrites any source that mentions `prefers-color-scheme` and
drops the width part. Images in one paragraph sit about 5px apart on github.com, paragraphs
about 21px apart; rows of one group share a paragraph.

| Role | Size (units) |
| --- | --- |
| readout numeral | Fraunces 600, 56 |
| row name | Fraunces 600, 28 |
| sentence | Inter 400, 20, line height 30 |
| data | JetBrains Mono 500, 16 |

Card: radius 18 (as the banners), 1 unit border, 40 units side padding, 30 top and bottom.

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
card. Dark: faint dot grid, vital-red trace (2 units, round joins) with a soft glow. Light: ECG
paper (small squares at 8% opacity, every fifth line 16%) as a plain rectangle without outline
or radius, trace in strong ink. Motion: the trace draws once left to right in about 2.4
seconds, then a dot at the current week pulses. `prefers-reduced-motion` shows the finished trace.

Size: desktop plot region about 250 units high, card about 360; phone plot about 170.

Readouts, right of the trace on desktop (x 812 to 1160, one line per label) and under it on
phones (rows of equal height: numeral in a 160-unit column, label right of it on at most two
lines):

- `contributions, last 12 months`
- `pull requests merged in public repos` (precisely: in public repositories outside my own
  account; the alt text says so)
- `pull request reviews given`

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
  files keep sentences at 14px, the alt text states every fact, and the Stack block stays
  as searchable text. Revisit if a second link per row is ever needed.
- In Safari an SVG image follows the OS color scheme, not GitHub's theme setting. Accepted:
  Chrome and Firefox follow GitHub's setting, and the mismatch needs a fixed GitHub theme
  that differs from the OS.

## Data rules

- Only public data. Every search carries `is:public`; the workflow uses the default
  `GITHUB_TOKEN`, which cannot see private repositories anyway.
- A number that cannot be fetched keeps its last value from `data.json`; the build never
  writes a guess or a zero in its place.
- Every image has alt text that states the same facts as the picture.
