"""Fail the workflow when Notion data has gone stale.

This script looks for a database titled "Daily Steps" in Notion and
exits non-zero when the most recently edited row is older than
`FRESHNESS_MAX_DAYS` (default 5).
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

	rows = notion.databases.query(
		database_id=db_id,
		sorts=[{"timestamp": "last_edited_time", "direction": "descending"}],
		page_size=1,
	).get("results", [])

	if not rows:
		print(f"Freshness check: {DATABASE_TITLE} is empty.")
		sys.exit(1)

	newest_iso = rows[0].get("last_edited_time")
	if not newest_iso:
		print("Freshness check: newest row has no last_edited_time.")
		sys.exit(1)

	newest = datetime.fromisoformat(newest_iso.replace("Z", "+00:00"))
	age = datetime.now(timezone.utc) - newest

	print(
		f"Freshness check: newest {DATABASE_TITLE} edit is {age.days} days old, limit is {MAX_DAYS}."
	)

	if age > timedelta(days=MAX_DAYS):
		print("Data is stale. Failing the run so the board raises the lamp.")
		sys.exit(1)

	print("Data is fresh.")
	sys.exit(0)


if __name__ == "__main__":
	main()
