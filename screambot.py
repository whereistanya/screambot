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

  while True:
    events = slack_client.rtm_read()
    for event in events:
      text = None
      # Only react to new messages and message edits.
      if event['type'] == 'message' and "subtype" not in event:
        text = event["text"]
      elif event['type'] == 'message' and event['subtype'] == 'message_changed':
        text = event["message"]["text"]

      if text:
        response = responses.create_response(text, bot_id)
        if response:
          slack_client.api_call("chat.postMessage", channel=event["channel"], text=response)
    time.sleep(RTM_READ_DELAY)

main()
