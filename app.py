#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import threading
import time
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

import responses
import secret

# Try to import Google Cloud Logging. Only works if running in GCP; use local logging otherwise.
try:
  import google.cloud.logging
  HAS_GCP_LOGGING = True
except ImportError:
  HAS_GCP_LOGGING = False

# User cache for responding with people's names.
user_cache = {}
cache_generation_time = 0
CACHE_REFRESH_TIME = 60 * 60 * 24  # 24 hours


def setup_local_logging():
  """Configure local console logging with standard format."""
  logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
  )


def refresh_cache(app):
  """Refresh the user cache from Slack API.

  Args:
    app: The Bolt App instance
  Returns:
    dict: Map of user IDs to usernames
    float: Unix timestamp when cache was generated
  """
  global user_cache, cache_generation_time

  try:
    result = app.client.users_list()
    if not result.get('ok') or 'members' not in result:
      logging.warning("Couldn't get a user cache")
      return user_cache, time.time()

    new_cache = {}
    for member in result['members']:
      uid = member['id']
      name = member['name']
      try:
        profile_name = member['profile'].get('first_name') or member['profile'].get('real_name')
      except KeyError:
        profile_name = None

      if profile_name:
        new_cache[uid] = profile_name
      else:
        new_cache[uid] = name

    user_cache = new_cache
    cache_generation_time = time.time()
    logging.info("User cache refreshed with %d users", len(user_cache))
    return user_cache, cache_generation_time

  except Exception as e:
    logging.error("Error refreshing user cache: %s", e)
    return user_cache, time.time()

def handle_message(message, say, bot_user_id):
  """Process a message and respond if appropriate.

  Args:
    message: Message event dict from Slack
    say: Bolt's say function to send responses
    bot_user_id: This bot's user ID
  """
  text = message.get('text', '')
  user_id = message.get('user')

  username = user_cache.get(user_id)

  # Generate response using existing logic
  response = responses.create_response(text, bot_user_id, speaker=username)

  if response:
    say(response)


def main():
  # Set up logging: Google Cloud Logging if in GCP, otherwise local logging
  logging.getLogger().name = "screambot"

  if HAS_GCP_LOGGING:
    try:
      logclient = google.cloud.logging.Client()
      logclient.setup_logging()
      logging.info("Google Cloud Logging enabled")
    except Exception as e:
      # If GCP logging fails (e.g., no credentials), fall back to local logging
      setup_local_logging()
      logging.warning("Google Cloud Logging setup failed (%s), using local logging", e)
  else:
    # Not in GCP, use local logging
    setup_local_logging()
    logging.info("Using local logging (Google Cloud Logging not available)")

  logging.info("Screambot starting up...")

  # Initialize Slack Bolt app
  app = App(token=secret.SLACK_BOT_TOKEN)

  # Authenticate with Slack and get bot user ID
  try:
    auth_result = app.client.auth_test()
    bot_user_id = auth_result['user_id']
    logging.info("Bot User ID: %s", bot_user_id)
  except Exception as e:
    logging.error("Failed to authenticate with Slack: %s", e)
    logging.error("Check that SLACK_BOT_TOKEN in secret.py is valid")
    sys.exit(1)

  # Register message handler.
  @app.event("message")
  def handle_message_events(event, say):
    """Handle messages in channels where screambot is present."""
    # Skip bot messages and message subtypes we don't care about
    if event.get('bot_id'):
      return

    # Only handle regular messages and edited messages
    subtype = event.get('subtype')
    if subtype and subtype not in ['message_changed']:
      return

    # For edited messages, get the actual message content
    if subtype == 'message_changed':
      message = event.get('message', {})
    else:
      message = event

    handle_message(message, say, bot_user_id)

  # Initialize user cache so we can respond with people's set usernames.
  refresh_cache(app)

  # Start a background task to refresh cache periodically
  def refresh_cache_periodically():
    """Background task to refresh user cache every 24 hours."""
    while True:
      time.sleep(CACHE_REFRESH_TIME)
      refresh_cache(app)

  cache_thread = threading.Thread(target=refresh_cache_periodically, daemon=True)
  cache_thread.start()

  # Start the Socket Mode handler with auto-reconnect
  logging.info("Screambot = yes!")

  # Socket Mode handler automatically reconnects on connection loss
  # But we wrap it in a loop to restart if it exits unexpectedly
  while True:
    try:
      handler = SocketModeHandler(app, secret.SLACK_APP_TOKEN)
      logging.info("Connecting to Slack...")
      handler.start()  # Blocks until connection lost
    except KeyboardInterrupt:
      logging.info("Received interrupt, shutting down...")
      break
    except Exception as e:
      logging.error("Socket Mode handler crashed: %s", e)
      logging.info("Reconnecting in 10 seconds...")
      time.sleep(10)

  logging.info("Screambot shutting down")


if __name__ == "__main__":
  main()
