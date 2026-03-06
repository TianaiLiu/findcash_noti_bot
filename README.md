# Instagram Story → Discord Notifier

Sends a Discord notification whenever a public Instagram account posts a new story.

---

## Quick Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create a Discord Bot
1. Go to https://discord.com/developers/applications → **New Application**
2. Navigate to **Bot** → **Add Bot**
3. Under **Token**, click **Reset Token** and copy it
4. Under **Privileged Gateway Intents**, enable **Message Content Intent**
5. Go to **OAuth2 → URL Generator**, select `bot` scope + `Send Messages` permission
6. Open the generated URL and invite the bot to your server

### 3. Get your Channel ID
- In Discord, enable **Developer Mode** (Settings → Advanced)
- Right-click the target channel → **Copy Channel ID**

### 4. Edit `config.py` (for security)
Never commit your bot token! Instead, edit `config.py`:

```python
INSTAGRAM_USERNAME     = "nasa"               # Any public Instagram username
DISCORD_BOT_TOKEN      = "YOUR_TOKEN_HERE"    # From step 2
DISCORD_CHANNEL_ID     = 123456789012345678   # From step 3
CHECK_INTERVAL_SECONDS = 60                   # Poll frequency in seconds
```

### 5. Run the bot
```bash
python bot.py
```

---

## Changing the Instagram Account
Just update the variable in `config.py`:
```python
INSTAGRAM_USERNAME = "newaccountname"
```
Restart the bot and it will start monitoring the new account immediately.

---

## Notes
- Only **public** Instagram accounts are supported (no login required)
- The bot skips stories that already exist on startup to avoid spam
- Instagram rate-limits aggressive polling — 60 seconds is a safe interval
- Stories disappear after 24 hours on Instagram; the bot only alerts on new ones
>>>>>>> 391f23a (Initial commit: Add Discord bot for Instagram story notifications with secure config)
