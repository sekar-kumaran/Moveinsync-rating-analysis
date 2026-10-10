#!/usr/bin/env python3
"""
collect_reviews.py
------------------
Collects Google Play Store reviews for the MoveInSync employee transport app
(com.moveinsync.ets) using the google-play-scraper library.

Usage:
    python src/collect_reviews.py [--app-id APP_ID] [--count COUNT] [--lang LANG] [--country COUNTRY]

Features:
- Paginated collection (newest + most_relevant sorts)
- Deduplication by review ID
- Incremental updates (appends new reviews, skips existing)
- Timestamped metadata
- Graceful error handling and logging
"""

import os
import sys
import json
import csv
import time
import logging
import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_CSV = RAW_DIR / "google_play_reviews.csv"
META_JSON = RAW_DIR / "collection_metadata.json"
ERROR_LOG = RAW_DIR / "collection_errors.log"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(ERROR_LOG), mode="a", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_APP_ID = "com.moveinsync.ets"
DEFAULT_LANG = "en"
DEFAULT_COUNTRY = "in"
SLEEP_BETWEEN_BATCHES = 2.0  # seconds – polite pacing
MAX_CONTINUATION_TOKENS = 50  # max pagination loops per sort order


CSV_FIELDNAMES = [
    "review_id",
    "app_id",
    "review_text",
    "star_rating",
    "review_date",
    "review_date_ts",
    "last_updated",
    "app_version",
    "reviewer_id_hash",  # hashed – not raw reviewer ID
    "developer_reply",
    "developer_reply_date",
    "language",
    "country",
    "source_platform",
    "sort_order",
    "collection_timestamp",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _hash_id(value: str) -> str:
    """One-way hash of reviewer identifier for privacy."""
    return hashlib.sha256(value.encode()).hexdigest()[:16] if value else ""


def _safe_str(value) -> str:
    if value is None:
        return ""
    return str(value).replace("\r", " ").replace("\n", " ").strip()


def _safe_date(value) -> str:
    """Convert datetime or None to ISO 8601 string."""
    if value is None:
        return ""
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _record_from_raw(raw: dict, app_id: str, lang: str, country: str, sort_order: str) -> dict:
    """Normalise a raw google-play-scraper review dict into our schema."""
    reviewer_name = raw.get("userName", "") or ""
    reviewer_id_hash = _hash_id(reviewer_name)

    return {
        "review_id": _safe_str(raw.get("reviewId", "")),
        "app_id": app_id,
        "review_text": _safe_str(raw.get("content", "")),
        "star_rating": raw.get("score", ""),
        "review_date": _safe_date(raw.get("at")),
        "review_date_ts": raw.get("at").timestamp() if isinstance(raw.get("at"), datetime) else "",
        "last_updated": _safe_date(raw.get("repliedAt")),  # closest proxy
        "app_version": _safe_str(raw.get("appVersion", "")),
        "reviewer_id_hash": reviewer_id_hash,
        "developer_reply": _safe_str(raw.get("replyContent", "")),
        "developer_reply_date": _safe_date(raw.get("repliedAt")),
        "language": lang,
        "country": country,
        "source_platform": "google_play",
        "sort_order": sort_order,
        "collection_timestamp": datetime.now(timezone.utc).isoformat(),
    }


def load_existing_ids(path: Path) -> set:
    """Return the set of review_ids already in the output CSV."""
    existing = set()
    if not path.exists():
        return existing
    try:
        with open(path, "r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                rid = row.get("review_id", "").strip()
                if rid:
                    existing.add(rid)
    except Exception as exc:
        logger.warning("Could not read existing IDs: %s", exc)
    return existing


# ---------------------------------------------------------------------------
# Collection
# ---------------------------------------------------------------------------

def collect_with_pagination(
    app_id: str,
    lang: str,
    country: str,
    sort_order_name: str,
    sort_order_value: int,
    existing_ids: set,
    target_count: int = 5000,
) -> list[dict]:
    """
    Paginate through Google Play reviews using continuation tokens.

    Returns a list of new (not already seen) normalised records.
    """
    from google_play_scraper import reviews, Sort

    collected = []
    seen_in_run = set()
    continuation_token = None
    batch_num = 0
    consecutive_all_seen = 0  # stop early if we keep hitting duplicates

    logger.info(
        "Starting collection: sort=%s, lang=%s, country=%s, target=%d",
        sort_order_name, lang, country, target_count,
    )

    while True:
        batch_num += 1
        try:
            result, continuation_token = reviews(
                app_id,
                lang=lang,
                country=country,
                sort=sort_order_value,
                count=200,
                continuation_token=continuation_token,
            )
        except Exception as exc:
            logger.error("Batch %d failed (sort=%s): %s", batch_num, sort_order_name, exc)
            break

        if not result:
            logger.info("No results returned at batch %d. Stopping.", batch_num)
            break

        new_in_batch = 0
        for raw in result:
            rid = _safe_str(raw.get("reviewId", ""))
            if not rid or rid in existing_ids or rid in seen_in_run:
                continue
            rec = _record_from_raw(raw, app_id, lang, country, sort_order_name)
            collected.append(rec)
            seen_in_run.add(rid)
            new_in_batch += 1

        logger.info(
            "Batch %d: fetched=%d, new=%d, total_new=%d",
            batch_num, len(result), new_in_batch, len(collected),
        )

        if new_in_batch == 0:
            consecutive_all_seen += 1
            if consecutive_all_seen >= 3:
                logger.info("3 consecutive batches with no new reviews. Stopping early.")
                break
        else:
            consecutive_all_seen = 0

        if continuation_token is None:
            logger.info("No continuation token. All pages exhausted.")
            break

        if len(collected) >= target_count:
            logger.info("Reached target count %d.", target_count)
            break

        if batch_num >= MAX_CONTINUATION_TOKENS:
            logger.warning("Reached max pagination limit (%d).", MAX_CONTINUATION_TOKENS)
            break

        time.sleep(SLEEP_BETWEEN_BATCHES)

    return collected


def save_records(records: list[dict], path: Path, existing_ids: set):
    """Append new records to the output CSV, writing header if file is new."""
    if not records:
        logger.info("No new records to save.")
        return 0

    file_exists = path.exists()
    written = 0

    with open(path, "a", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDNAMES, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        for rec in records:
            if rec["review_id"] not in existing_ids:
                writer.writerow(rec)
                existing_ids.add(rec["review_id"])
                written += 1

    logger.info("Saved %d new records to %s", written, path)
    return written


def write_metadata(meta: dict, path: Path):
    """Write or update collection metadata JSON."""
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as fh:
                existing = json.load(fh)
        except Exception:
            existing = {}
    else:
        existing = {}

    existing.update(meta)
    # Accumulate run history
    if "run_history" not in existing:
        existing["run_history"] = []
    existing["run_history"].append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "records_added": meta.get("records_added_this_run", 0),
        "total_records": meta.get("total_records_in_file", 0),
    })

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(existing, fh, indent=2, default=str)
    logger.info("Metadata written to %s", path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Collect MoveInSync Google Play reviews")
    parser.add_argument("--app-id", default=DEFAULT_APP_ID, help="Google Play app ID")
    parser.add_argument("--lang", default=DEFAULT_LANG, help="Language code (default: en)")
    parser.add_argument("--country", default=DEFAULT_COUNTRY, help="Country code (default: in)")
    parser.add_argument("--count", type=int, default=5000, help="Target reviews per sort order")
    args = parser.parse_args()

    try:
        from google_play_scraper import Sort
    except ImportError:
        logger.error("google-play-scraper not installed. Run: pip install google-play-scraper")
        sys.exit(1)

    app_id = args.app_id
    lang = args.lang
    country = args.country

    logger.info("=" * 60)
    logger.info("MoveInSync Review Collector")
    logger.info("App ID: %s | Lang: %s | Country: %s", app_id, lang, country)
    logger.info("Output: %s", OUTPUT_CSV)
    logger.info("=" * 60)

    existing_ids = load_existing_ids(OUTPUT_CSV)
    logger.info("Loaded %d existing review IDs.", len(existing_ids))

    total_added = 0
    run_errors = []

    sort_configs = [
        ("NEWEST", Sort.NEWEST),
        ("MOST_RELEVANT", Sort.MOST_RELEVANT),
    ]

    for sort_name, sort_val in sort_configs:
        try:
            records = collect_with_pagination(
                app_id=app_id,
                lang=lang,
                country=country,
                sort_order_name=sort_name,
                sort_order_value=sort_val,
                existing_ids=existing_ids,
                target_count=args.count,
            )
            added = save_records(records, OUTPUT_CSV, existing_ids)
            total_added += added
        except Exception as exc:
            msg = f"Sort={sort_name} failed: {exc}"
            logger.error(msg)
            run_errors.append(msg)

    # Count total records now in file
    total_in_file = len(load_existing_ids(OUTPUT_CSV))

    metadata = {
        "app_id": app_id,
        "source_platform": "google_play",
        "collection_method": "google-play-scraper (Python)",
        "language": lang,
        "country": country,
        "records_added_this_run": total_added,
        "total_records_in_file": total_in_file,
        "last_collection_timestamp": datetime.now(timezone.utc).isoformat(),
        "output_file": str(OUTPUT_CSV),
        "errors_this_run": run_errors,
        "notes": (
            "google-play-scraper retrieves only publicly visible reviews. "
            "The platform does not expose a complete historical dataset. "
            "Actual Play Store review count may be higher than collected."
        ),
    }
    write_metadata(metadata, META_JSON)

    logger.info("=" * 60)
    logger.info("Collection complete. Added: %d | Total in file: %d", total_added, total_in_file)
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
