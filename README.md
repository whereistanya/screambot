# Screambot

Screambot just freaks out about everything all the time, on slack. It's not anything clever with AI,
it's just a maze of twisty regexs. Hey, we make our own fun.

### Prerequisites

1. Python 3.7 or higher
2. A Slack workspace where you have admin permissions
3. Google Cloud Platform account (for logging, optional)

### Step 1: Create/Update Slack App

1. Go to https://api.slack.com/apps
2. Select your existing Screambot app (or create a new one)

3. **Enable Socket Mode**:
   - Go to **Settings** → **Socket Mode**
   - Toggle **Enable Socket Mode** to ON

4. **Create App-Level Token**:
   - Go to **Basic Information** → **App-Level Tokens**
   - Click **Generate Token and Scopes**
   - Name it "screambot-socket" (or any name you like)
   - Add scope: `connections:write`
   - Click **Generate**
   - Copy the token (starts with `xapp-`) - you'll need this for `secret.py`

5. **Get Bot Token**:
   - Go to **OAuth & Permissions**
   - Copy the **Bot User OAuth Token** (starts with `xoxb-`)

6. **Configure Bot Scopes** (OAuth & Permissions):
   - `app_mentions:read` - See when the bot is mentioned
   - `chat:write` - Send messages
   - `channels:history` - Read channel messages
   - `groups:history` - Read private channel messages
   - `im:history` - Read direct messages
   - `users:read` - Get user info for friendly names

7. **Configure Event Subscriptions**:
   - Go to **Event Subscriptions**
   - Subscribe to bot events:
     - `message.channels` - Messages in channels
     - `message.groups` - Messages in private channels
     - `message.im` - Direct messages to the bot

8. **Install/Reinstall App**:
   - Go to **Install App**
   - Click **Reinstall to Workspace** (if updating existing app)
   - Authorize the requested permissions

9. **Invite Bot to Channels**:
   - In Slack, type `/invite @screambot` in any channel where you want it active

### Step 2: Configure Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/whereistanya/screambot.git
   cd screambot
   ```

2. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

3. Create `secret.py` with your tokens:
   SLACK_BOT_TOKEN = "xoxb-your-bot-token-here"
   SLACK_APP_TOKEN = "xapp-your-app-token-here"
   ```

4. Test locally:
   ```bash
   python3 app.py
   ```

   You should see:
   ```
   Screambot starting up...
   User cache refreshed with X users
   Screambot = yes!
   ```

5. Test in Slack by sending a message: `@screambot hello`

### Step 3: Deploy to Production (GCE VM)

#### On your GCE VM:

1. Install just like locally but also configure systemd


2. **Copy the new systemd service file**:
   ```bash
   sudo cp config/screambot.service /etc/systemd/system/screambot.service
   # Edit paths if your working directory is different
   sudo nano /etc/systemd/system/screambot.service
   sudo systemctl daemon-reload
   ```

3. **Stop the old bot** (if running):
   ```bash
   sudo systemctl stop screambot
   ```

4. **Start the new bot**:
   ```bash
   sudo systemctl start screambot
   sudo systemctl status screambot
   ```

5. **Enable auto-start on boot**:
   ```bash
   sudo systemctl enable screambot
   ```

