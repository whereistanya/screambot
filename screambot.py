#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import time
import re
import sys
from string import Template

from slackclient import SlackClient

import responses
import secret

RTM_READ_DELAY = 0.2 # 0.2 second delay between reading from RTM
COMMAND_REGEX = "^<@(|[WU].+?)> (.+)"

def refresh_cache(slack_client):
  """This calls the Slack API, so use sparingly.

  Args:
    slack_client: (SlackClient) an authenticated connection to the slack API
  Returns:
    ({string: string}) A map of userids to usernames
    (float) The unix timestamp at which this user cache was generated
  """
  user_cache = {}
  userlist = slack_client.api_call('users.list')
  for member in userlist['members']:
    uid = member['id']
    name = member['name']
    try:
      profile_name = member['profile']['first_name']
    except KeyError:
      profile_name = member['profile']['real_name']
    if profile_name:
      user_cache[uid] = profile_name
    else:
      user_cache[uid] = name
  return user_cache, time.time()


def main():
  #print("Token is %s\n" % secret.SLACK_BOT_TOKEN)
  slack_client = SlackClient(secret.SLACK_BOT_TOKEN)
  if slack_client.rtm_connect(with_team_state=False):
    logging.info("Scream bot = yes!")
  else:
    logging.error("Connection failed. Exception traceback printed above.")
    sys.exit(1)
  try:
    bot_id = slack_client.api_call("auth.test")["user_id"]
  except ValueError, e:
    logging.error("Couldn't auth: %s\n", e)
    sys.exit(1)

  user_cache, generation_time = refresh_cache(slack_client)

  refresh_time = 60 * 60 * 24 # one day
  while True:
    if time.time() - generation_time > refresh_time:
      user_cache, generation_time = refresh_cache(slack_client)
    events = slack_client.rtm_read()
    for event in events:
      text = None
      # Only react to new messages and message edits.
      if event['type'] == 'message' and "subtype" not in event:
        text = event["text"]
      elif event['type'] == 'message' and event['subtype'] == 'message_changed':
        text = event["message"]["text"]

      if text:
        # If we've got a username for whoever called screambot, pass it into the
        # response generator. The cache is updated every 24, so might be missing
        # users or username changes since then. We could call the API again when usernames
        # are missing, but it doesn't feel quite worth it...
        username = None
        if event['user']:
          uid = event['user']
          if uid in user_cache:
            username = user_cache[uid]
          
        response = responses.create_response(text, bot_id, speaker=username)
        if response:
          slack_client.api_call("chat.postMessage", channel=event["channel"], text=response)
    time.sleep(RTM_READ_DELAY)

main()
