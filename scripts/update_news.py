#!/usr/bin/env python3
"""
Build data/news.json for Fantasy Command Center.

The updater intentionally stores only RSS/feed metadata supplied by publishers:
headline/title, short feed description, source URL, publication time and a
small heuristic fantasy-impact classification. It does not scrape full articles.
"""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "news.json"

SOURCES = [
    {
        "name": "CBS Sports NFL",
        "url": "https://www.cbssports.com/rss/headlines/nfl",
        "confidence": 0.88,
    },
    {
        "name": "ProFootballTalk / NBC Sports",
        "url": "https://feeds.feedburner.com/pftalk",
        "confidence": 0.84,
    },
    {
        "name": "NFL.com News",
        "url": "https://www.nfl.com/news?service=rss",
        "confidence": 0.92,
    },
]

UA = "FantasyCommandCenter-NewsBot/1.0 (+GitHub Actions; RSS metadata only)"

TAG_RE = re.compile(r"<[^>]+>")
WS_RE = re.compile(r"\s+")

RULES = [
    (
        "availability",
        "negative",
        -10,
        re.compile(
            r"\b(ruled out|placed on (?:injured reserve|ir)|season[- ]ending|"
            r"torn (?:acl|achilles|mcl)|will miss (?:the )?season|surgery|"
            r"suspended|commissioner'?s exempt)\b",
            re.I,
        ),
    ),
    (
        "availability",
        "negative",
        -6,
        re.compile(
            r"\b(out indefinitely|expected to miss|will miss|won't play|will not play|"
            r"did not practice|dnp|concussion protocol|week[- ]to[- ]week)\b",
            re.I,
        ),
    ),
    (
        "injury",
        "watch",
        -3,
        re.compile(
            r"\b(questionable|limited|day[- ]to[- ]day|hamstring|ankle|groin|"
            r"knee injury|foot injury|shoulder injury|calf injury|back injury|"
            r"left practice|injured|injury)\b",
            re.I,
        ),
    ),
    (
        "availability",
        "positive",
        4,
        re.compile(
            r"\b(cleared to play|expected to play|will play|full practice|"
            r"activated from (?:ir|pup)|activated off (?:ir|pup)|returns? to practice|"
            r"back at practice|ready for week|good to go)\b",
            re.I,
        ),
    ),
    (
        "role",
        "positive",
        4,
        re.compile(
            r"\b(named (?:the )?starter|will start|starting (?:quarterback|running back)|"
            r"lead back|workhorse|more touches|larger role|expanded role|promoted)\b",
            re.I,
        ),
    ),
    (
        "role",
        "watch",
        -2,
        re.compile(
            r"\b(benched|demoted|reduced role|fewer touches|loses starting job|"
            r"loses starter role)\b",
            re.I,
        ),
    ),
    (
        "transaction",
        "watch",
        0,
        re.compile(r"\b(traded|trade|signed|released|waived|claimed)\b", re.I),
    ),
]

NOISE_PATTERNS = [
    re.compile(r"\b(mvp|rookie of the year|offensive rookie of the year|defensive rookie of the year)\b.*\b(odds|bet|betting|market|board|favorite)", re.I),
    re.compile(r"\b(odds board|betting odds|best bets?|prop bets?|sportsbook|wager|parlay)\b", re.I),
    re.compile(r"\b(power rankings?|mock draft|draft grades?|way-too-early|award odds)\b", re.I),
]

def is_fantasy_noise(title: str, summary: str) -> bool:
    text = f"{title} {summary[:250]}"
    return any(pattern.search(text) for pattern in NOISE_PATTERNS)



def clean_text(value: str | None) -> str:
    value = html.unescape(value or "")
    value = TAG_RE.sub(" ", value)
    return WS_RE.sub(" ", value).strip()


def fetch(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": UA,
            "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, text/html;q=0.5",
        },
    )
    with urllib.request.urlopen(req, timeout=25) as response:
        return response.read()


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()

    try:
        d = parsedate_to_datetime(value)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except Exception:
        pass

    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except Exception:
        return None


def text_of(node: ET.Element | None, names: list[str]) -> str:
    if node is None:
        return ""
    for child in list(node):
        local = child.tag.split("}")[-1].lower()
        if local in names:
            return "".join(child.itertext()).strip()
    return ""


def link_of(node: ET.Element) -> str:
    for child in list(node):
        local = child.tag.split("}")[-1].lower()
        if local != "link":
            continue
        href = child.attrib.get("href")
        if href:
            return href.strip()
        txt = (child.text or "").strip()
        if txt:
            return txt
    return ""


def parse_feed(blob: bytes, source: dict) -> list[dict]:
    # Some publishers return ordinary HTML to bots instead of RSS. In that case,
    # fail this source cleanly and let the other feeds continue.
    stripped = blob.lstrip()
    if not stripped.startswith(b"<"):
        return []

    try:
        root = ET.fromstring(blob)
    except ET.ParseError:
        return []

    items = []
    candidates = [
        e
        for e in root.iter()
        if e.tag.split("}")[-1].lower() in {"item", "entry"}
    ]

    for item in candidates:
        title = clean_text(text_of(item, ["title"]))
        summary = clean_text(
            text_of(item, ["description", "summary", "content", "content:encoded"])
        )
        url = link_of(item)
        published_raw = text_of(
            item, ["pubdate", "published", "updated", "dc:date", "date"]
        )
        published = parse_date(published_raw)

        if not title:
            continue

        items.append(
            {
                "title": title[:500],
                "summary": summary[:900],
                "url": url,
                "published_at": published.isoformat().replace("+00:00", "Z")
                if published
                else None,
                "source": source["name"],
                "source_confidence": source["confidence"],
            }
        )
    return items


def classify(title: str, summary: str, source_confidence: float) -> dict:
    # Weight the title more heavily than the summary to reduce accidental
    # sentiment spillover from articles mentioning multiple players.
    text = f"{title} {summary[:350]}"
    category = "news"
    impact = "neutral"
    score = 0

    for cat, imp, pts, pattern in RULES:
        if pattern.search(text):
            category, impact, score = cat, imp, pts
            break

    return {
        "category": category,
        "impact": impact,
        "score_adjustment": score,
        "confidence": round(float(source_confidence), 2),
    }


def valid_url(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme in {"http", "https"} and bool(p.netloc)
    except Exception:
        return False


def normalize_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def main() -> int:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=7)
    articles = []
    source_status = []

    for source in SOURCES:
        try:
            blob = fetch(source["url"])
            parsed = parse_feed(blob, source)
            source_status.append(
                {"source": source["name"], "ok": True, "articles": len(parsed)}
            )
            articles.extend(parsed)
        except Exception as exc:
            source_status.append(
                {
                    "source": source["name"],
                    "ok": False,
                    "articles": 0,
                    "error": str(exc)[:180],
                }
            )

    dedup = {}
    for article in articles:
        published = parse_date(article.get("published_at"))
        if published and published < cutoff:
            continue

        url = article.get("url") or ""
        if url and not valid_url(url):
            url = ""
        article["url"] = url

        if is_fantasy_noise(article["title"], article.get("summary", "")):
            continue

        article.update(
            classify(
                article["title"],
                article.get("summary", ""),
                article.get("source_confidence", 0.7),
            )
        )

        key = normalize_title(article["title"])
        existing = dedup.get(key)
        if not existing:
            dedup[key] = article
            continue

        # Prefer a newer timestamp; if equal/unknown, prefer higher-confidence source.
        old_dt = parse_date(existing.get("published_at"))
        new_dt = parse_date(article.get("published_at"))
        replace = False
        if new_dt and (not old_dt or new_dt > old_dt):
            replace = True
        elif (article.get("confidence") or 0) > (existing.get("confidence") or 0):
            replace = True
        if replace:
            dedup[key] = article

    final = list(dedup.values())
    final.sort(
        key=lambda a: parse_date(a.get("published_at"))
        or datetime(1970, 1, 1, tzinfo=timezone.utc),
        reverse=True,
    )
    final = final[:150]

    payload = {
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "lookback_days": 7,
        "article_count": len(final),
        "sources": source_status,
        "articles": final,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    ok_sources = sum(1 for s in source_status if s["ok"])
    print(f"Wrote {len(final)} articles to {OUT}")
    print(f"Sources succeeded: {ok_sources}/{len(source_status)}")
    return 0 if ok_sources else 1


if __name__ == "__main__":
    raise SystemExit(main())
