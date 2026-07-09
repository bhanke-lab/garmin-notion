# Garmin to Notion

Sync your Garmin fitness data to Notion databases. Runs twice a day, on GitHub Actions or on your own machine, with GitHub auditing data freshness either way.

> This is a fork of [fly-labs/garmin-to-notion](https://github.com/fly-labs/garmin-to-notion) with enhancements. See [Fork Enhancements](#fork-enhancements) below.

![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![Sync: GitHub Actions](https://img.shields.io/badge/sync-GitHub%20Actions-purple)

## Fork Enhancements

This fork adds the following on top of the original:

### New Database: Fitness Summary

- Training Readiness: Garmin's daily readiness score (0-100)
- Training Level: PRIME / HIGH / MODERATE / LOW / POOR classification
- LT Heart Rate: lactate threshold heart rate
- Race Predictions: estimated 5K, 10K, Half Marathon, and Marathon times

### Enhanced Sleep Tracking

- Stress data: `Stress Avg` and `Stress Max` per night (uses `avgStressLevel` from the Garmin API; `overallStressLevel` returns NULL)
- HRV data: `HRV Avg` (heart rate variability) and `HRV Status` (BALANCED / LOW / UNBALANCED / POOR)
- SpO2: blood oxygen saturation percentage
- Respiration: average respiration rate
- Bed Time / Wake Time: sleep and wake timestamps
- Computed Sleep Score: custom quality score (1-100) based on:
  - Duration (40%): 100 if 7 to 9 hours, linear ramp from 4h to 7h and 9h to 11h
  - Deep Sleep % (25%): optimal ~20%, drops 4 pts per 1% deviation
  - REM % (25%): optimal ~22%, drops 4 pts per 1% deviation
  - Awake Penalty (10%): 0 min = 100, 30+ min = 0

### Enhanced Activity Tracking

- VO2 Max: per-activity VO2 Max reading (when reported by Garmin)
- VO2 Type: formula property that categorizes as "Running" or "Cycling" for split trend analysis
- Hour Block: 2-hour time window (e.g. `16:00-18:00`) for workout timing analysis
- Day of Week: for weekly pattern analysis

### Notion Template with 18+ Chart Views

The Notion AI prompt creates a complete dashboard with:

- Trend lines: Sleep Score, Garmin Score, Stress, HRV, Resting HR, VO2 Max (split by Running/Cycling), Training Readiness
- Distribution donuts: activity type, calories by sport, distance by sport, workout time of day, HRV Status, Training Level
- Correlation charts: Sleep vs Stress, HRV by Stress Level, Avg HR by Activity Type, Calories by Day of Week
- Weekly Training Load: calorie-based weekly volume tracking
- All charts include descriptive captions

### Sync Runner Toggle

The sync can run on GitHub Actions or on your own machine, switched by a single repository variable with no code change. See [Where the Sync Runs](#where-the-sync-runs). Local mode exists because Garmin rate-limits the shared IP ranges that GitHub's hosted runners use; a machine on a normal home or office connection logs in without trouble.

### Freshness Monitoring

Every workflow run ends with `scripts/check_freshness.py`. It finds the Daily Steps database, reads the date on the newest row, and fails the run when that date is older than `FRESHNESS_MAX_DAYS` (default 5). Daily Steps gets a row every day whether or not you work out, so it is the honest signal. The check measures data dates rather than edit times, so clicking around in Notion cannot vouch for a sync that never happened. A red run means data stopped landing, whatever the cause.

### Bug Fixes

- Fixed Garmin stress API key: `avgStressLevel` (not `overallStressLevel`, which returns NULL)
- Garmin token cache saves under a unique key per run, so the save step no longer fails against an immutable key

### Performance

- Configurable summary window: by default the Activity Summary sync only recomputes the current and previous month plus the current year, instead of every month/year bucket since you started tracking. Cuts a typical sync from ~5 minutes to ~30 seconds. Tune via `SUMMARY_WINDOW_MONTHS` (default `2`, set to `9999` for a full rebuild).

## Features

- Activities: distance, pace, power, HR, training effect, VO2 Max, with emoji icons and heatmap properties
- Personal Records: fastest 1K, 5K, 10K, longest run/ride, and more
- Daily Steps: step count, goal, distance
- Sleep: duration, deep/light/REM/awake stages, resting HR, HRV, stress, SpO2, computed quality score
- Fitness Summary: daily training readiness, training level, LT heart rate, race predictions (new in this fork)
- Workouts: categorized workout log with modality and intensity derived from activities
- Activity Summary: monthly and yearly aggregations with lifestyle averages (sleep, steps, HR)
- 60+ activity types: running, cycling, swimming, strength, BJJ, climbing, winter sports, and more
- Auto-discovery: finds your Notion databases by name, no manual IDs needed
- Timezone-aware: configurable via the `TIMEZONE` variable, all timestamps are correct
- Runs twice a day unattended, and tells on itself when data goes stale

## Setup Guide

### Step 1: Fork this repository

Click Fork on GitHub to create your own copy.

### Step 2: Set up your Notion template

Option A, Notion AI (recommended):

1. Open a new Notion page
2. Copy the full contents of [`docs/notion-ai-prompt.txt`](docs/notion-ai-prompt.txt)
3. Paste it into Notion AI. It creates the complete template with all 6 databases, 18+ chart views, and board/calendar views
4. Follow the post-creation checklist in [`docs/notion-template-setup.md`](docs/notion-template-setup.md) to convert date filters to relative

Option B, duplicate template: coming soon, a public template you can duplicate in one click.

### Step 3: Create Notion integration

1. Go to [notion.so/profile/integrations](https://www.notion.so/profile/integrations)
2. Click New integration, name it "Garmin Sync", select Internal
3. Copy the integration token (starts with `ntn_`)
4. Go to your Fitness Tracker page in Notion, open the `...` menu, choose Connect to, pick Garmin Sync

All inline databases inherit access automatically. No need to connect each one individually.

### Step 4: Add GitHub Secrets

Go to your fork's Settings > Secrets and variables > Actions > Secrets and add:

| Secret | Description |
|---|---|
| `GARMIN_EMAIL` | Your Garmin Connect email |
| `GARMIN_PASSWORD` | Your Garmin Connect password |
| `NOTION_TOKEN` | Your Notion integration token |
| `GARMIN_TOKENS` | Optional. Saved Garmin OAuth tokens so runs can reuse a session instead of logging in fresh |

### Step 5: Set Variables (optional)

Go to Settings > Secrets and variables > Actions > Variables and add:

| Variable | Default | Description |
|---|---|---|
| `TIMEZONE` | `UTC` | Your IANA timezone (e.g. `America/New_York`, `Europe/London`) |
| `GARMIN_DAYS_BACK` | `30` | Days of sleep/steps history to sync |
| `SUMMARY_WINDOW_MONTHS` | `2` | How many recent months the Activity Summary recomputes (set `9999` for a full rebuild) |
| `SYNC_RUNNER` | `github` | Set to `local` to move the sync to your own machine; GitHub then only audits freshness |
| `FRESHNESS_MAX_DAYS` | `5` | Fail the run when the newest Daily Steps row is older than this many days |

### Step 6: Run

Go to the Actions tab, Garmin to Notion Sync, Run workflow. The manual run accepts a `days_back` input for one-off backfills.

Your data will appear in Notion within a few minutes. After that, the sync runs automatically twice a day.

## Where the Sync Runs

A repository variable named `SYNC_RUNNER` decides who does the work. The schedule never changes; the variable changes what the scheduled run does.

### GitHub mode (default)

With `SYNC_RUNNER` unset or set to `github`, the scheduled workflow syncs from a GitHub-hosted runner and then runs the freshness check. Nothing else to set up.

The catch: hosted runners share Azure IP ranges with thousands of other workflows, including plenty of other Garmin sync forks, and Garmin rate-limits logins by source IP. Runs can fail with HTTP 429 through no fault of yours or your code's. The sync treats a 429 as a clean skip, and the freshness check decides whether it matters: occasional skips pass quietly, a pattern of skips that lets the data go stale turns the run red.

### Local mode

Set `SYNC_RUNNER` to `local`. Scheduled GitHub runs then skip every Garmin step and only run the freshness check, about 30 seconds of auditing per run. Your machine does the actual syncing from an IP Garmin trusts. If the local schedule dies silently, the audit goes red within `FRESHNESS_MAX_DAYS` days.

To hand the job back to GitHub, set the variable to `github` or delete it, then remove the local schedule.

Run the schedule on one machine at a time. Double-syncing is harmless to the data since everything upserts, but there is no reason to double your Garmin login traffic.

#### Windows (Task Scheduler)

From the project root in PowerShell:

```powershell
.\scripts\register_sync_task.ps1
```

This registers a task named "Garmin Notion Sync" at 7:05 AM and 8:05 PM daily. It uses the Interactive logon type, so it runs while you are logged in (a locked screen counts) without storing your password, and missed runs fire at the next unlock. To change the schedule, edit the two trigger times in the script and run it again.

The task calls `scripts/run_sync.ps1`, which uses the project's `.venv` and `.env` and appends output to `sync_log.txt` in the project root.

Test it end to end:

```powershell
Start-ScheduledTask -TaskName "Garmin Notion Sync"
Get-ScheduledTaskInfo -TaskName "Garmin Notion Sync" | Select-Object LastRunTime, LastTaskResult
Get-Content sync_log.txt -Tail 40
```

Remove it:

```powershell
Unregister-ScheduledTask -TaskName "Garmin Notion Sync" -Confirm:$false
```

#### macOS (launchd)

Clone the repo, set up `.venv` and `.env` the same way, then:

```bash
cp scripts/com.bhanke.garmin-notion.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.bhanke.garmin-notion.plist
```

Same 7:05 and 20:05 schedule. launchd fires missed triggers when the Mac wakes, so a sleeping laptop syncs on wake instead of skipping. Edit the path inside the plist if your project lives somewhere other than `~/Projects/garmin-notion`. Remove with `launchctl unload` on the same path.

## How It Works

```
Garmin Connect API
│
├──→ Activities DB ──→ Workouts DB ──┐
├──→ Personal Records DB             ├──→ Activity Summary DB
├──→ Daily Steps DB ─────────────────┘         (monthly/yearly)
├──→ Sleep DB
└──→ Fitness Summary DB (new)
```

Activities, Personal Records, Daily Steps, Sleep, and Fitness Summary are synced independently from the Garmin API. Workouts are derived from Activities. Activity Summary aggregates data from Workouts, Daily Steps, and Sleep into monthly and yearly overviews.

## Supported Activities

| Category | Activities | Tracked Metrics |
|---|---|---|
| Running | Running, Treadmill, Trail, Track, Ultra | Distance, Pace, HR, Training Effect, VO2 Max |
| Cycling | Outdoor, Indoor, Mountain Biking, Gravel, E-Bike | Distance, Power, Duration, VO2 Max |
| Swimming | Lap Swimming, Open Water | Distance, Duration, Calories |
| Strength & Fitness | Strength Training, Crossfit, Functional Training, HIIT | Duration, Calories, Training Effect |
| Combat | BJJ / MMA, Boxing, Kickboxing | Duration, Calories, Intensity |
| Racquet Sports | Tennis, Padel, Badminton, Pickleball, Squash, Table Tennis | Duration, Calories |
| Team Sports | Soccer, Basketball, Volleyball, Football, Rugby, Hockey | Duration, Calories |
| Winter Sports | Skiing, Snowboarding, Cross Country Skiing, Ice Skating | Duration, Distance, Calories |
| Water Sports | Kayaking, Surfing, Stand Up Paddleboarding | Duration, Distance |
| Climbing | Rock Climbing, Bouldering, Indoor Climbing, Mountaineering | Duration, Calories |
| Walking | Walking, Hiking, Speed Walking | Steps, Distance |
| Yoga & Mindfulness | Yoga, Pilates, Stretching, Meditation | Duration, Calories |
| Rowing | Rowing, Indoor Rowing | Distance, Power, Duration |
| Other | Golf, Dance, Skateboarding, Multi Sport, Triathlon | Duration, Calories |

## Configuration

### GitHub Secrets

| Secret | Description |
|---|---|
| `GARMIN_EMAIL` | Your Garmin Connect email (required) |
| `GARMIN_PASSWORD` | Your Garmin Connect password (required) |
| `NOTION_TOKEN` | Your Notion integration token (required) |
| `GARMIN_TOKENS` | Saved Garmin OAuth tokens (optional) |

### GitHub Variables (optional)

| Variable | Default | Description |
|---|---|---|
| `TIMEZONE` | `UTC` | IANA timezone for activity timestamps |
| `GARMIN_DAYS_BACK` | `30` | Days of sleep/steps history to sync |
| `SUMMARY_WINDOW_MONTHS` | `2` | Months of history the Activity Summary recomputes per run (set `9999` to rebuild every period) |
| `SYNC_RUNNER` | `github` | `github` runs the sync on Actions; `local` skips it there and only audits freshness |
| `FRESHNESS_MAX_DAYS` | `5` | Staleness threshold for the freshness check |

### Database IDs (optional, auto-discovered by default)

If auto-discovery doesn't work, you can set these as secrets:

| Secret | Database |
|---|---|
| `NOTION_DB_ID` | Activities |
| `NOTION_PR_DB_ID` | Personal Records |
| `NOTION_STEPS_DB_ID` | Daily Steps |
| `NOTION_SLEEP_DB_ID` | Sleep |
| `NOTION_WORKOUTS_DB_ID` | Workouts |
| `NOTION_SUMMARY_DB_ID` | Activity Summary |

## Running Locally

For one-off manual runs. The scheduled local setup is covered in [Where the Sync Runs](#where-the-sync-runs).

```bash
# install dependencies
pip install -r requirements.txt

# copy and configure environment
cp .env.example .env
# edit .env with your credentials

# run all syncs
PYTHONPATH=src python -m garmin_to_notion all

# run a specific sync
PYTHONPATH=src python -m garmin_to_notion activities
PYTHONPATH=src python -m garmin_to_notion records
PYTHONPATH=src python -m garmin_to_notion steps
PYTHONPATH=src python -m garmin_to_notion sleep
PYTHONPATH=src python -m garmin_to_notion fitness_summary
PYTHONPATH=src python -m garmin_to_notion workouts
PYTHONPATH=src python -m garmin_to_notion summary

# cleanup duplicate workouts (dry run first)
PYTHONPATH=src python -m garmin_to_notion cleanup
PYTHONPATH=src python -m garmin_to_notion cleanup --execute

# verbose output
PYTHONPATH=src python -m garmin_to_notion all -v
```

Windows (PowerShell):

```powershell
cd C:\path\to\garmin-notion
$env:PYTHONPATH = "src"
python -m garmin_to_notion all
```

## Project Structure

```
src/garmin_to_notion/
    __init__.py          # Package version
    __main__.py          # CLI entry point
    config.py            # Settings and env validation
    clients.py           # Garmin + Notion client setup
    log.py               # Logging configuration
    notion_helpers.py    # Shared Notion utilities
    formatters.py        # Data formatting (pace, duration, etc.)
    mappings.py          # Activity emojis, modality maps, constants
    syncers/
        activities.py        # Garmin -> Activities DB
        personal_records.py  # Garmin -> Personal Records DB
        daily_steps.py       # Garmin -> Daily Steps DB
        sleep.py             # Garmin -> Sleep DB
        fitness_summary.py   # Garmin -> Fitness Summary DB (new)
        workouts.py          # Activities DB -> Workouts DB
        summary.py           # Workouts+Steps+Sleep -> Activity Summary DB
    tools/
        cleanup_duplicates.py  # Deduplicate Workouts DB
scripts/
    check_freshness.py               # Fails the workflow when data goes stale
    run_sync.ps1                     # Local sync wrapper for Task Scheduler
    register_sync_task.ps1           # Registers the Windows schedule
    com.bhanke.garmin-notion.plist   # macOS launchd schedule
.github/workflows/
    sync.yml             # Scheduled sync plus freshness audit
```

## Troubleshooting

### Charts show errors

Run the Notion AI update prompt ([`docs/notion-ai-update-prompt.txt`](docs/notion-ai-update-prompt.txt)) to recreate all views and charts. Make sure your databases have data first; charts won't render on empty databases.

### Wrong activity times

Set the `TIMEZONE` variable to your IANA timezone (e.g. `America/New_York`). If you already have activities with wrong times, re-run `python -m garmin_to_notion activities`; it detects and fixes timezone mismatches automatically.

### Calendar views show empty months

Notion calendar views require a Date property. If a month appears empty, check that the sync has run and populated data for that period. For sleep and steps, increase `GARMIN_DAYS_BACK` to backfill older data.

### Activity Summary shows zero steps or sleep

Activity Summary aggregates from the Workouts, Daily Steps, and Sleep databases. Make sure all three syncs have run at least once. Run `python -m garmin_to_notion all` to sync everything, then `python -m garmin_to_notion summary` to regenerate summaries.

### Activity Summary missing old months after backfilling activities

By default the summary sync only recomputes the last 2 months plus the current year. If you backfilled older activities, force a one-time full rebuild by setting `SUMMARY_WINDOW_MONTHS=9999` (as a repo Variable or local env var) and running the sync. Set it back to `2` afterward.

### Sleep sync is slow on first run

The first sync fetches `GARMIN_DAYS_BACK` days of sleep data (default 30). For large backfills (e.g. `GARMIN_DAYS_BACK=3650`), the first run calls the Garmin API for each day without existing data. Subsequent syncs skip existing dates and are near-instant.

### Stress data shows NULL

The Garmin API key for daily stress is `avgStressLevel`, not `overallStressLevel` (which returns NULL). Already fixed in this fork.

### Auto-discovery can't find databases

Make sure the Notion integration is connected to the Fitness Tracker page (not individual databases). Database names must match exactly: Activities, Personal Records, Daily Steps, Sleep, Fitness Summary, Workouts, Activity Summary.

### Rate limiting (HTTP 429)

Garmin rate-limits login attempts by source IP, and GitHub-hosted runners share Azure IP ranges with everyone else's workflows, including other Garmin sync forks. A 429 on Actions is environmental, not a bug in your setup. The sync skips the run cleanly and the freshness check tracks whether it matters. Do not manually re-run for 2 to 4 hours; every attempt is another login against a hot limit. If 429s persist for days and the freshness check goes red, switch to local mode (see [Where the Sync Runs](#where-the-sync-runs)). The same code that 429s from a datacenter logs in fine from a home or office connection.

### The freshness check fails

That is the feature working: no new data has landed in `FRESHNESS_MAX_DAYS` days. Check that whichever side is supposed to be syncing (GitHub or your local schedule) is actually running. In local mode, check `sync_log.txt` in the project root. After a long outage, run one manual sync with a `days_back` value larger than the gap so the backfill covers it.

### Troubleshooting: "Could not find databases" despite a correct token

Symptom: the sync logs

    Could not find databases: Activities, Personal Records, Daily Steps, Sleep, Workouts, ActivitySummary

even though the Notion integration is connected to the Fitness Tracker page and `NOTION_TOKEN` in `.env` is correct.

Cause: `python-dotenv` does NOT override variables already present in the environment (`load_dotenv(override=False)` is the default). A stale `NOTION_TOKEN` set at the Windows User or Machine scope (or exported in a shell profile on macOS/Linux) wins over `.env`. If that token belongs to a different or old integration, the discovery search 401s.

Diagnose (PowerShell):

    "session: $env:NOTION_TOKEN"
    "user:    " + [Environment]::GetEnvironmentVariable("NOTION_TOKEN","User")
    "machine: " + [Environment]::GetEnvironmentVariable("NOTION_TOKEN","Machine")

If any print a token that is not the one in `.env`, clear it:

    # session
    Remove-Item Env:\NOTION_TOKEN -ErrorAction SilentlyContinue
    # user scope (no admin needed)
    [Environment]::SetEnvironmentVariable("NOTION_TOKEN", $null, "User")
    # machine scope (run PowerShell as Administrator)
    [Environment]::SetEnvironmentVariable("NOTION_TOKEN", $null, "Machine")

macOS / Linux:

    unset NOTION_TOKEN          # session
    # then remove any `export NOTION_TOKEN=...` line from ~/.zshrc or ~/.bash_profile

Open a fresh terminal and re-run. Alternatively, change `load_dotenv()` to `load_dotenv(override=True)` in the code so `.env` always wins.

Check a token directly against the Notion API (PowerShell):

    $token = "ntn_xxx"
    $headers = @{ Authorization = "Bearer $token"; "Notion-Version" = "2022-06-28" }
    (Invoke-RestMethod -Uri "https://api.notion.com/v1/users/me" -Headers $headers).bot
    $body = '{"filter":{"property":"object","value":"database"}}'
    (Invoke-RestMethod -Method Post -Uri "https://api.notion.com/v1/search" -Headers $headers -Body $body -ContentType "application/json").results | ForEach-Object { $_.title.plain_text }

## Acknowledgements

This project builds on the work of [Chloe Voyer](https://github.com/chloevoyer/garmin-to-notion), who created the original Garmin-to-Notion sync, and the extended version by [FlyLabs](https://github.com/fly-labs/garmin-to-notion). This fork adds Fitness Summary tracking, enhanced sleep metrics (HRV, stress, SpO2), VO2 Max tracking, a computed sleep score, a full Notion dashboard with 18+ chart views, a local/GitHub sync runner toggle, and freshness monitoring.

Other projects that inspired this work:

- [python-garminconnect](https://github.com/cyberjunky/python-garminconnect): Garmin API wrapper
- [n-kratz/garmin-notion](https://github.com/n-kratz/garmin-notion): alternative Garmin-Notion integration

## License

MIT License. See [LICENSE](LICENSE) for details.
