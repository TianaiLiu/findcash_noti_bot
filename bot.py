import discord
from discord.ext import tasks
import instaloader
import asyncio
import os
from datetime import datetime, timezone, time
import pytz

# Try to import from config.py (local), fallback to environment variables (Replit)
try:
    from config import INSTAGRAM_USERNAME, DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, POLL_INTERVAL_SECONDS, ACTIVE_WINDOW_START, ACTIVE_WINDOW_END, TIMEZONE
except ImportError:
    # Running on Replit or environment without config.py
    INSTAGRAM_USERNAME = os.getenv("INSTAGRAM_USERNAME", "nasa")
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
    DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
    POLL_INTERVAL_SECONDS = int(os.getenv("POLL_INTERVAL_SECONDS", "60"))
    TIMEZONE = os.getenv("TIMEZONE", "America/Toronto")
    ACTIVE_WINDOW_START = time(11, 30)  # Default 11:30
    ACTIVE_WINDOW_END = time(13, 0)     # Default 13:00

# ── Internal state ───────────────────────────────────────────────
intents        = discord.Intents.default()
client         = discord.Client(intents=intents)
loader         = instaloader.Instaloader()
seen_story_ids: set[int] = set()
first_run      = True
tz             = pytz.timezone(TIMEZONE)


# ────────────────────────────────────────────────────────────────
#  Helpers
# ────────────────────────────────────────────────────────────────

def is_within_active_window() -> bool:
    """Return True if the current local time falls inside the active window."""
    now = datetime.now(tz).time().replace(second=0, microsecond=0)
    if ACTIVE_WINDOW_START <= ACTIVE_WINDOW_END:
        # Normal window:  08:00 – 23:00
        return ACTIVE_WINDOW_START <= now <= ACTIVE_WINDOW_END
    else:
        # Overnight window: e.g. 22:00 – 02:00
        return now >= ACTIVE_WINDOW_START or now <= ACTIVE_WINDOW_END


def fetch_stories(username: str) -> list:
    """Fetch all current story items for a public Instagram account."""
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        stories = list(loader.get_stories(userids=[profile.userid]))
        return list(stories[0].get_items()) if stories else []
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"[ERROR] Instagram profile '{username}' does not exist.")
        return []
    except Exception as e:
        print(f"[ERROR] Could not fetch stories: {e}")
        return []


def format_time(t: time) -> str:
    return t.strftime("%H:%M")


# ────────────────────────────────────────────────────────────────
#  Main polling loop
# ────────────────────────────────────────────────────────────────

@tasks.loop(seconds=POLL_INTERVAL_SECONDS)
async def check_stories():
    global seen_story_ids, first_run

    now_str    = datetime.now(tz).strftime("%H:%M:%S")
    window_str = f"{format_time(ACTIVE_WINDOW_START)} – {format_time(ACTIVE_WINDOW_END)} ({TIMEZONE})"

    # ── Active-window gate ───────────────────────────────────────
    if not is_within_active_window():
        print(f"[{now_str}] 💤 Outside active window ({window_str}). Sleeping…")
        return
    # ────────────────────────────────────────────────────────────

    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if channel is None:
        print("[ERROR] Discord channel not found — check DISCORD_CHANNEL_ID.")
        return

    print(f"[{now_str}] 🔍 Checking stories for @{INSTAGRAM_USERNAME}…")
    story_items = fetch_stories(INSTAGRAM_USERNAME)

    new_stories: list = []
    current_ids: set[int] = set()

    for item in story_items:
        current_ids.add(item.mediaid)
        if item.mediaid not in seen_story_ids:
            new_stories.append(item)

    # First run: silently seed IDs so we don't re-announce existing stories
    if first_run:
        seen_story_ids = current_ids
        first_run      = False
        print(f"[INFO] Seeded {len(current_ids)} existing story ID(s). Watching for new ones…")
        return

    # Notify for every genuinely new story
    for item in new_stories:
        media_type = "📸 Photo" if not item.is_video else "🎥 Video"
        posted_at  = (
            item.date_utc
            .replace(tzinfo=timezone.utc)
            .astimezone(tz)
            .strftime("%Y-%m-%d %H:%M:%S")
        )

        embed = discord.Embed(
            title       = f"New Story from @{INSTAGRAM_USERNAME}!",
            url         = f"https://www.instagram.com/{INSTAGRAM_USERNAME}/",
            description = (
                f"{media_type} story posted at **{posted_at}**\n\n"
                f"[View Profile ↗](https://www.instagram.com/{INSTAGRAM_USERNAME}/)"
            ),
            color     = discord.Color.from_rgb(225, 48, 108),
            timestamp = datetime.now(timezone.utc),
        )
        embed.add_field(
            name  = "⏱ Poll interval",
            value = f"Every {POLL_INTERVAL_SECONDS}s",
            inline=True,
        )
        embed.add_field(
            name  = "🕐 Active window",
            value = window_str,
            inline=True,
        )
        embed.set_footer(text="Instagram Story Monitor")

        await channel.send(embed=embed)
        print(f"[NOTIFY] ✅ Sent notification for story ID {item.mediaid}")

    seen_story_ids = current_ids

    if not new_stories:
        print(f"[{now_str}] No new stories. Next check in {POLL_INTERVAL_SECONDS}s.")


# ────────────────────────────────────────────────────────────────
#  Bot startup
# ────────────────────────────────────────────────────────────────

@client.event
async def on_ready():
    print("=" * 55)
    print(f"  Bot online   : {client.user}")
    print(f"  Monitoring   : @{INSTAGRAM_USERNAME}")
    print(f"  Channel ID   : {DISCORD_CHANNEL_ID}")
    print(f"  Poll every   : {POLL_INTERVAL_SECONDS} seconds")
    print(f"  Active from  : {format_time(ACTIVE_WINDOW_START)}"
          f"  to  {format_time(ACTIVE_WINDOW_END)}  ({TIMEZONE})")
    print("=" * 55)
    check_stories.start()


if __name__ == "__main__":
    if DISCORD_BOT_TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        raise SystemExit(
            "[ERROR] Set DISCORD_BOT_TOKEN at the top of bot.py before running."
        )
    client.run(DISCORD_BOT_TOKEN)
