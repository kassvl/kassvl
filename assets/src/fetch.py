#!/usr/bin/env python3
"""Refresh assets/src/data.json from the GitHub API through the `gh` CLI.

No token is handled here: `gh` uses its own login, or GH_TOKEN in CI.
A field that cannot be fetched keeps its previous value. Exit code 1 only when
nothing could be fetched at all. `updated` changes only when a number changed.

Usage: python3 assets/src/fetch.py
"""
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE / "data.json"
USER = "kassvl"

# Explicit allowlist: a repository is shown only because it is listed here.
REPOS = [
    "nordstjernen-web/nordstjernen-sol-browser",
    "getsentry/relay",
    "istio/istio.io",
    "nordstjernen-web/southstar-browser",
]


def gql(query: str) -> dict:
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={query}"],
                         capture_output=True, text=True, timeout=90)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip()[:300])
    res = json.loads(out.stdout)
    if res.get("errors") and not res.get("data"):
        raise RuntimeError(str(res["errors"])[:300])
    return res["data"]


def fetch_calendar() -> dict:
    d = gql("""{ user(login: "%s") { contributionsCollection {
      totalPullRequestReviewContributions
      contributionCalendar { totalContributions weeks { firstDay contributionDays { date contributionCount } } }
    } } }""" % USER)["user"]["contributionsCollection"]
    cal = d["contributionCalendar"]
    weeks = [{"start": w["firstDay"], "count": sum(x["contributionCount"] for x in w["contributionDays"])}
             for w in cal["weeks"]]
    days = [x["contributionCount"] for w in cal["weeks"] for x in w["contributionDays"]]
    longest = run = 0
    for c in days:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    return {
        "weeks": weeks,
        "total": cal["totalContributions"],
        "active_days": sum(1 for c in days if c > 0),
        "longest_streak": longest,
        "reviews": d["totalPullRequestReviewContributions"],
    }


def count(q: str) -> int:
    d = gql('{ search(query: "%s", type: ISSUE, first: 1) { issueCount } }' % q)
    return d["search"]["issueCount"]


def fetch_repo(repo: str) -> dict:
    base = f"repo:{repo} is:pr is:public author:{USER}"
    d = gql("""{ repository(owner: "%s", name: "%s") { stargazerCount }
      merged: search(query: "%s is:merged sort:updated-desc", type: ISSUE, first: 50) {
        issueCount nodes { ... on PullRequest { title mergedAt } } }
      open: search(query: "%s is:open", type: ISSUE, first: 1) { issueCount } }"""
            % (*repo.split("/"), base, base))
    prs = [n for n in d["merged"]["nodes"] if n and n.get("mergedAt")]
    latest = max(prs, key=lambda n: n["mergedAt"]) if prs else None
    out = {
        "stars": d["repository"]["stargazerCount"],
        "merged": d["merged"]["issueCount"],
        "open": d["open"]["issueCount"],
    }
    if latest:  # otherwise the caller keeps the previous title and date
        out["latest_title"] = latest["title"]
        out["latest_merged"] = latest["mergedAt"][:10]
    return out


def numbers(d: dict) -> dict:
    """Everything except the `updated` stamp, for change detection."""
    return {k: v for k, v in d.items() if k != "updated"}


def main() -> int:
    old = json.loads(DATA.read_text()) if DATA.exists() else {}
    new = json.loads(json.dumps(old))
    ok = fail = 0

    def attempt(label, fn, store):
        nonlocal ok, fail
        try:
            store(fn())
            ok += 1
            print(f"ok    {label}")
        except Exception as e:  # keep the previous value
            fail += 1
            print(f"FAIL  {label}: {e}", file=sys.stderr)

    attempt("calendar", fetch_calendar, lambda v: new.update(calendar=v))
    attempt("merged outside own account",
            lambda: count(f"author:{USER} is:pr is:merged is:public -user:{USER}"),
            lambda v: new.update(merged_outside=v))
    new.setdefault("repos", {})
    for repo in REPOS:
        attempt(repo, lambda r=repo: fetch_repo(r), lambda v, r=repo: new["repos"].setdefault(r, {}).update(v))

    if ok == 0:
        print("nothing could be fetched", file=sys.stderr)
        return 1
    new["repos"] = {r: new["repos"][r] for r in REPOS if r in new["repos"]}
    new["updated"] = old.get("updated") if numbers(new) == numbers(old) and old.get("updated") \
        else dt.datetime.now(dt.timezone.utc).date().isoformat()
    text = json.dumps(new, indent=1, ensure_ascii=False) + "\n"
    if not DATA.exists() or DATA.read_text() != text:
        DATA.write_text(text)
    c = new.get("calendar", {})
    print(f"contributions {c.get('total')}, merged outside {new.get('merged_outside')}, "
          f"reviews {c.get('reviews')}, active days {c.get('active_days')}, streak {c.get('longest_streak')}, "
          f"updated {new['updated']}")
    for r, v in new["repos"].items():
        print(f"  {r}: stars {v['stars']}, merged {v['merged']}, open {v['open']}, latest {v.get('latest_merged')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
