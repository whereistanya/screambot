#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import re
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


def escape_slack_markup(text):
  """Escape Slack markup characters to prevent injection.

  Args:
    text: User-provided string that may contain Slack markup

  Returns:
    Escaped string safe for display
  """
  if not text:
    return text
  # Escape special Slack markup characters
  text = str(text).replace('&', '&amp;')
  text = text.replace('<', '&lt;')
  text = text.replace('>', '&gt;')
  return text


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

def show_command_management_ui(channel_id, user_id, app):
  """Show the command management UI using Block Kit.

  Args:
    channel_id: Slack channel ID to post the message in
    user_id: Slack user ID (for context)
    app: The Bolt App instance
  """
  from storage import get_storage
  from datetime import datetime

  storage = get_storage()
  commands = storage.list_all_commands()

  blocks = [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": f"📝 Custom Commands ({len(commands)})"
      }
    },
    {
      "type": "divider"
    }
  ]

  # Add each command as a section with delete button
  for cmd in commands:
    creator_name = user_cache.get(cmd['created_by'], 'Unknown')
    # Format timestamp if available
    created_at = cmd.get('created_at', 'Unknown date')
    if created_at and created_at != 'Unknown date':
      try:
        # Parse SQLite timestamp and format
        dt = datetime.fromisoformat(created_at.replace(' ', 'T'))
        created_at = dt.strftime('%b %d, %Y')
      except:
        pass

    # Escape user-provided content to prevent Slack markup injection
    safe_trigger = escape_slack_markup(cmd['trigger'])
    safe_response = escape_slack_markup(cmd['response'])

    blocks.append({
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": f"*\"{safe_trigger}\"* → \"{safe_response}\"\n_Created by {creator_name} on {created_at}_"
      },
      "accessory": {
        "type": "button",
        "text": {
          "type": "plain_text",
          "text": "Delete"
        },
        "style": "danger",
        "action_id": f"delete_command_{cmd['trigger']}",
        "confirm": {
          "title": {
            "type": "plain_text",
            "text": "Delete command?"
          },
          "text": {
            "type": "mrkdwn",
            "text": f"Are you sure you want to delete \"{safe_trigger}\"?\n\nThis cannot be undone."
          },
          "confirm": {
            "type": "plain_text",
            "text": "Delete"
          },
          "deny": {
            "type": "plain_text",
            "text": "Cancel"
          }
        }
      }
    })

  # Add "Create New Command" button
  blocks.append({
    "type": "divider"
  })
  blocks.append({
    "type": "actions",
    "elements": [
      {
        "type": "button",
        "text": {
          "type": "plain_text",
          "text": "➕ Create New Command"
        },
        "style": "primary",
        "action_id": "open_create_command_modal"
      }
    ]
  })

  # Post the message with blocks
  app.client.chat_postMessage(
    channel=channel_id,
    blocks=blocks,
    text=f"Custom Commands ({len(commands)})"  # Fallback text
  )

def handle_message(message, say, bot_user_id, app):
  """Process a message and respond if appropriate.

  Args:
    message: Message event dict from Slack
    say: Bolt's say function to send responses
    bot_user_id: This bot's user ID
    app: The Bolt App instance (for posting Block Kit messages)
  """
  text = message.get('text', '')
  user_id = message.get('user')

  username = user_cache.get(user_id)

  # Generate response using existing logic
  response = responses.create_response(text, bot_user_id, speaker=username, user_id=user_id)

  if response == "__OPEN_MANAGE_COMMANDS_UI__":
    # Show the command management UI instead of a text response
    show_command_management_ui(message.get('channel'), user_id, app)
  elif response:
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

    handle_message(message, say, bot_user_id, app)

  # Initialize user cache so we can respond with people's set usernames.
  refresh_cache(app)

  # Initialize storage manager
  from storage import get_storage
  storage = get_storage()
  logging.info("Storage initialized")

  # Make storage available to responses module
  responses.set_storage(storage)

  # Register Slack action handlers for custom commands UI

  @app.action("open_create_command_modal")
  def handle_create_command_button(ack, body, client):
    """Handle click on 'Create New Command' button."""
    ack()

    # Open modal
    client.views_open(
      trigger_id=body["trigger_id"],
      view={
        "type": "modal",
        "callback_id": "create_command_modal",
        "title": {
          "type": "plain_text",
          "text": "Create Custom Command"
        },
        "submit": {
          "type": "plain_text",
          "text": "Create"
        },
        "close": {
          "type": "plain_text",
          "text": "Cancel"
        },
        "blocks": [
          {
            "type": "input",
            "block_id": "trigger_block",
            "label": {
              "type": "plain_text",
              "text": "Trigger phrase"
            },
            "element": {
              "type": "plain_text_input",
              "action_id": "trigger_input",
              "placeholder": {
                "type": "plain_text",
                "text": "e.g., panic or love"
              },
              "max_length": 100
            },
            "hint": {
              "type": "plain_text",
              "text": "Any command can be a template. Use $what in your response. 2-100 characters."
            }
          },
          {
            "type": "input",
            "block_id": "response_block",
            "label": {
              "type": "plain_text",
              "text": "Response"
            },
            "element": {
              "type": "plain_text_input",
              "action_id": "response_input",
              "multiline": True,
              "placeholder": {
                "type": "plain_text",
                "text": "e.g., I love $what SO MUCH!"
              },
              "max_length": 500
            },
            "hint": {
              "type": "plain_text",
              "text": "Use $what to capture extra text after the trigger. Max 500 characters."
            }
          }
        ]
      }
    )

  @app.action(re.compile("^delete_command_.*"))
  def handle_delete_command(ack, action, body, client):
    """Handle delete button clicks."""
    ack()

    # Extract trigger from action_id
    trigger = action["action_id"].replace("delete_command_", "")
    user_id = body["user"]["id"]

    if storage.delete_command(trigger, deleted_by=user_id):
      # Refresh the UI
      show_command_management_ui(body["channel"]["id"], user_id, app)

      # Send confirmation
      client.chat_postEphemeral(
        channel=body["channel"]["id"],
        user=user_id,
        text=f"✅ Deleted command \"{trigger}\""
      )
    else:
      client.chat_postEphemeral(
        channel=body["channel"]["id"],
        user=user_id,
        text=f"❌ Failed to delete command \"{trigger}\""
      )

  @app.view("create_command_modal")
  def handle_create_command_submission(ack, body, view, client):
    """Handle submission of the create command modal."""
    # Extract values
    trigger = view["state"]["values"]["trigger_block"]["trigger_input"]["value"]
    response_text = view["state"]["values"]["response_block"]["response_input"]["value"]
    user_id = body["user"]["id"]

    # Validate
    errors = {}
    if len(trigger) < 2:
      errors["trigger_block"] = "Trigger must be at least 2 characters"
    if len(trigger) > 100:
      errors["trigger_block"] = "Trigger must be 100 characters or less"
    if not response_text or len(response_text.strip()) == 0:
      errors["response_block"] = "Response cannot be empty"
    if len(response_text) > 500:
      errors["response_block"] = "Response must be 500 characters or less"

    if errors:
      ack(response_action="errors", errors=errors)
      return

    # Save to database
    success = storage.add_command(trigger.lower(), response_text, user_id)

    if success:
      ack()
      # Send confirmation (in DM to user)
      try:
        safe_trigger = escape_slack_markup(trigger)
        safe_response = escape_slack_markup(response_text)
        client.chat_postMessage(
          channel=user_id,
          text=f"✅ Created command \"{safe_trigger}\" → \"{safe_response}\""
        )
      except Exception as e:
        # Fallback if DM fails
        logging.warning(f"Failed to send DM to {user_id}: {e}")
        logging.info(f"Created command '{trigger}' by {user_id}")
    else:
      ack(response_action="errors", errors={
        "trigger_block": "Failed to create command. It may already exist."
      })

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

  # Close storage
  storage.close()
  logging.info("Storage closed")


if __name__ == "__main__":
  main()
