#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import time
import re
import sys
from slackclient import SlackClient

import secret
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
COMMAND_REGEX = "^<@(|[WU].+?)> (.+)"


def create_response(message, bot_id):
  """Decide whether this is an event worth responding to.

  Screambot replies in the following circumstances:
    * @screambot scream thing: responds "THING"
    * @screambot hate thing: responds "I hate thing""
    * @screambot what anything: responds with info about screambot
    * @screambot otherverb thing: responds "Don't know how"
    * @otheruser sentence containing @screambot: responds "you're talking about me"
    * other sentence containing @screambot: TBD
  """
# Only trigger on sentences containing "screambot" or @screambot's UID.
  if bot_id.lower() not in message.lower() and "screambot" not in message.lower():
    return

  # First handle commands starting with a username
  matches = re.search(COMMAND_REGEX, message)
  if matches:
    user = matches.group(1)
    command = matches.group(2)
    if user == bot_id:
      if command.lower() in ["scream", "holler", "freak out"]:
        return "AAAARRGGHHHHHHHHHHHHHH"
      if command.lower() in ["help"]:
        return "We all need help sometimes and that's ok."
      if command.lower() in ["lose it", "lose your shit"]:
        return "I am kind of losing my shit right now?"
      if command.lower() in ["can you even?"]:
        return "I literally can't even."
      if command.lower() in ["thank you", "thanks"]:
        return "Glad to help <3"
      if command.lower() in [":heart:", "i love you", "we love you", "<3"]:
        return ":heart:"
      if command.lower().startswith("hug"):
        return ":virtualhug:"
      if command.lower().startswith("flip"):
        return "(╯°□°）╯︵ ┻━┻)"
      if command.lower().startswith("scream "):
        return command.partition(' ')[2].upper()
      if command.lower().startswith("hate "):
        return "I hate " + command.partition(' ')[2] + " SO MUCH. Ugh, the worst."
      if "code" in command.lower() or "github" in command.lower():
        return "My code's at https://github.com/whereistanya/screambot. Send Tanya a PR."
      else:
        response = "I don't know how to %s" % command
        return response
    else:
      return "You're talking about me <3"
 
  # Not a direct command, just a sentence with "screambot" in it.
  if message.lower().startswith("what"):
    return ("Hi, I'm screambot. Tell me to scream things. I'm running on " +
           "Tanya's GCE VM. I see all traffic on any channel I'm invited to, " +
           "but I promise I don't log anything. You can see my code at " +
           "https://github.com/whereistanya/screambot")

  if message.lower().startswith("thank"):
    return "Any time."

  if "code" in message.lower() or "github" in message.lower():
    return "My code's at https://github.com/whereistanya/screambot. Add something! Send Tanya a PR."

  if ":heart:" in message.lower() or "love" in message.lower():
    return ":heart_eyes:"

  return "Want me to do something? Start your message with @screambot."

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
      if "subtype" in event:
        continue
      response = create_response(event["text"], bot_id)
      if response:
        # print "Got %s and responding %s." % (event["text"], response)
        slack_client.api_call("chat.postMessage", channel=event["channel"], text=response)
      time.sleep(RTM_READ_DELAY)

main()
