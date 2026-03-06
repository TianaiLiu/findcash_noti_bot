import discord
from discord.ext import tasks
import instaloader
import asyncio
import os
from datetime import datetime, timezone
from config import INSTAGRAM_USERNAME, DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, CHECK_INTERVAL_SECONDS

intents = discord.Intents.default()
client  = discord.Client(intents=intents)
loader  = instaloader.Instaloader()

seen_story_ids: set[int] = set()
first_run = True


def fetch_stories(username: str) -> list[instaloader.Story]:
    """Fetch current stories for a public Instagram account."""
    try:
        profile = instaloader.Profile.from_username(loader.context, username)
        stories = list(loader.get_stories(userids=[profile.userid]))
        return stories[0].get_items() if stories else []
    except instaloader.exceptions.ProfileNotExistsException:
        print(f"[ERROR] Instagram profile '{username}' does not exist.")
        return []
    except Exception as e:
        print(f"[ERROR] Could not fetch stories: {e}")
        return []


@tasks.loop(seconds=CHECK_INTERVAL_SECONDS)
async def check_stories():
    global seen_story_ids, first_run

    channel = client.get_channel(DISCORD_CHANNEL_ID)
    if channel is None:
        print("[ERROR] Discord channel not found. Check DISCORD_CHANNEL_ID.")
        return

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Checking stories for @{INSTAGRAM_USERNAME}...")
    story_items = fetch_stories(INSTAGRAM_USERNAME)

    new_stories = []
    current_ids = set()

    for item in story_items:
        current_ids.add(item.mediaid)
        if item.mediaid not in seen_story_ids:
            new_stories.append(item)

    # On first run, just seed the known IDs — don't spam old stories
    if first_run:
        seen_story_ids = current_ids
        first_run = False
        count = len(current_ids)
        print(f"[INFO] Seeded {count} existing story ID(s). Watching for new ones...")
        return

    # Send a notification for each genuinely new story
    for item in new_stories:
        media_type = "📸 Photo" if not item.is_video else "🎥 Video"
        posted_at  = item.date_utc.replace(tzinfo=timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M:%S")

        embed = discord.Embed(
            title=f"New Story from @{INSTAGRAM_USERNAME}!",
            url=f"https://www.instagram.com/{INSTAGRAM_USERNAME}/",
            description=(
                f"{media_type} story posted at **{posted_at}**\n\n"
                f"[View Profile](https://www.instagram.com/{INSTAGRAM_USERNAME}/)"
            ),
            color=discord.Color.from_rgb(225, 48, 108),  # Instagram pink
            timestamp=datetime.now(timezone.utc),
        )
        embed.set_footer(text="Instagram Story Monitor")

        await channel.send(embed=embed)
        print(f"[NOTIFY] New story sent for @{INSTAGRAM_USERNAME} (ID: {item.mediaid})")

    seen_story_ids = current_ids


@client.event
async def on_ready():
    print(f"[BOT] Logged in as {client.user} (ID: {client.user.id})")
    print(f"[BOT] Monitoring Instagram account: @{INSTAGRAM_USERNAME}")
    print(f"[BOT] Posting to channel ID: {DISCORD_CHANNEL_ID}")
    print(f"[BOT] Checking every {CHECK_INTERVAL_SECONDS} seconds")
    check_stories.start()


if __name__ == "__main__":
    if DISCORD_BOT_TOKEN == "YOUR_DISCORD_BOT_TOKEN_HERE":
        raise SystemExit("[ERROR] Please set DISCORD_BOT_TOKEN in bot.py before running.")
    client.run(DISCORD_BOT_TOKEN)
