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

RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
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
      if event['type'] != 'message':
        continue
      print event
      if "subtype" in event and event['subtype'] != 'message_changed':
        continue
      response = responses.create_response(event["text"], bot_id)
      if response:
        # print "Got %s and responding %s." % (event["text"], response)
        slack_client.api_call("chat.postMessage", channel=event["channel"], text=response)
      time.sleep(RTM_READ_DELAY)

main()
