"""Fail the workflow when Notion data has gone stale.

Looks up the "Daily Steps" database, finds its date property, and exits
non-zero when the newest row's date is older than FRESHNESS_MAX_DAYS
(default 5). Uses the row's date value, not last_edited_time, so manual
edits in Notion cannot mask stale data.
"""

import os
import sys
from datetime import datetime, timedelta, timezone

from notion_client import Client

MAX_DAYS = int(os.environ.get("FRESHNESS_MAX_DAYS", "5"))
DATABASE_TITLE = "Daily Steps"


def find_database(notion):
    results = notion.search(
        query=DATABASE_TITLE,
        filter={"property": "object", "value": "database"},
    ).get("results", [])

    for db in results:
        title = "".join(t.get("plain_text", "") for t in db.get("title", []))
        if title == DATABASE_TITLE:
            return db.get("id")

    return None


def find_date_property(notion, db_id):
    props = notion.databases.retrieve(database_id=db_id).get("properties", {})
    date_props = [name for name, p in props.items() if p.get("type") == "date"]
    if "Date" in date_props:
        return "Date"
    return date_props[0] if date_props else None


def main():
    token = os.environ.get("NOTION_TOKEN")
    if not token:
        print("Freshness check: NOTION_TOKEN is not set.")
        sys.exit(1)

    notion = Client(auth=token)
    db_id = find_database(notion)
    if db_id is None:
        print(f"Freshness check: could not find the {DATABASE_TITLE} database.")
        sys.exit(1)

    date_prop = find_date_property(notion, db_id)
    if date_prop is None:
        print(f"Freshness check: {DATABASE_TITLE} has no date property.")
        sys.exit(1)

    rows = notion.databases.query(
        database_id=db_id,
        sorts=[{"property": date_prop, "direction": "descending"}],
        page_size=1,
    ).get("results", [])

    if not rows:
        print(f"Freshness check: {DATABASE_TITLE} is empty.")
        sys.exit(1)

    value = rows[0].get("properties", {}).get(date_prop, {}).get("date") or {}
    newest_iso = value.get("start")
    if not newest_iso:
        print(f"Freshness check: newest row has no {date_prop} value.")
        sys.exit(1)

    newest = datetime.fromisoformat(newest_iso.replace("Z", "+00:00"))
    if newest.tzinfo is None:
        newest = newest.replace(tzinfo=timezone.utc)
    age = datetime.now(timezone.utc) - newest

    print(
        f"Freshness check: newest {DATABASE_TITLE} row is dated {newest_iso}, "
        f"{age.days} days old, limit is {MAX_DAYS}."
    )

    if age > timedelta(days=MAX_DAYS):
        print("Data is stale. Failing the run so the board raises the lamp.")
        sys.exit(1)

    print("Data is fresh.")
    sys.exit(0)


if __name__ == "__main__":
    main()
