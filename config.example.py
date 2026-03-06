# ================================================================
#  CONFIGURATION TEMPLATE — Copy this and rename to config.py
# ================================================================
from datetime import time

INSTAGRAM_USERNAME  = "USERNAME"                        # 👈 Any public Instagram username
DISCORD_BOT_TOKEN   = "YOUR_DISCORD_BOT_TOKEN_HERE"           # 👈 Your Discord bot token
DISCORD_CHANNEL_ID  = 12345678910111213141516                     # 👈 Your Discord channel ID (integer)

# ── Polling interval ─────────────────────────────────────────────
# How many seconds to wait between each Instagram check.
POLL_INTERVAL_SECONDS = 60          # 👈 e.g. 30, 60, 120, 300 …

# ── Active window ────────────────────────────────────────────────
# The bot ONLY polls Instagram between START and END each day.
# Outside this window it sleeps silently.
# Use 24-hour format:  time(HH, MM)
ACTIVE_WINDOW_START = time(22, 0)    # 👈 Start polling at 11:30
ACTIVE_WINDOW_END   = time(2, 0)     # 👈 Stop  polling at 13:00
# Supports windows that cross midnight, e.g. time(22,0) → time(2,0)

# ── Timezone ─────────────────────────────────────────────────────
# All times above are interpreted in this timezone.
# Full list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
TIMEZONE = "America/New_York"        # 👈 e.g. "America/New_York", "Europe/London"
