#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from string import Template

COMMAND_REGEX = "^<@(|[WU].+?)> (.+)"

# It's a command to @screambot and this is the entire thing.
STANDALONE_COMMANDS = {
  "botsnack": ":cookie:",
  "freak out": "*breathes into a paper bag*",
  "lose it": "I am kind of losing my shit right now?",
  "lose your shit": "I am kind of losing my shit right now?",
  "scream": "AAAARRGGHHHHHHHHHHHHHH",
  "thank you": "Glad to help <3",
  "thanks": "Any time, friend.",
  ":heart:": ":heart:",
  ":poop:": "Seriously.",
  "hug": ":virtualhug:",
  "flip": "(╯°□°）╯︵ ┻━┻)",
  "<3": "Right back at you <3",
}

# It's a direct command to @screambot and it starts with this.
# "$what" will be replaced with the thing to scream about.
# TODO: Add "$who" and figure out how to talk to.
STARTER_COMMANDS = {
  "freak out about ": "I am LOSING MY SHIT about $what right now.",
  "lose it about ": "AGH what is the deal with $what?",
  "hug ": ":virtualhug: for $what",
  "flip ": "╯°□°）╯︵ ┻━�",
  "hate ": "I hate $what SO MUCH. Ugh, the worst.", 
  "I love you": "It's mutual, I promise you.",
  # look, I know this is terrible, but I'm too lazy to handle nice little functions today.
  "scream ": "FUNCTION:UPPERCASE $what",
  "help": "FUNCTION:HELP",
  "what can you do?": "FUNCTION:HELP",
}

# It's a direct command to @screambot and it contains this text.
CONTAIN_COMMANDS = {
  "botsnack": ":cookie:",
  "code": "My code's at https://github.com/whereistanya/screambot. Send Tanya a PR. :female_technologist:",
  "github": "My code's at https://github.com/whereistanya/screambot. Send Tanya a PR. :female_technologist:",
  "can you even": "I literally can't even.",
}

# It's not a command but it contains the word screambot and this text.
CONVERSATION = {
  "botsnack": ":cookie:",
  "code": "My code's at https://github.com/whereistanya/screambot. Send Tanya a PR.",
  "github": "My code's at https://github.com/whereistanya/screambot. Send Tanya a PR.",
  "thank": "Any time.",
  ":heart:": ":heart_eyes:",
  "love": ":heart_eyes:",
}

def help_message():
  """Returns a user message explaining what this is."""
  commands = set()
  for s in STANDALONE_COMMANDS.keys():
    commands.add(s)
  for s in STARTER_COMMANDS.keys():
    commands.add(s.rstrip(" "))

  return ("Hi, I'm Screambot. I'm running on Tanya's GCE VM. I see all " +
         "traffic on any channel I'm invited to, but I promise I don't log "
         "anything. You can see and modify my code at " +
         "https://github.com/whereistanya/screambot\n" +
         "Commands: " + "; ".join(sorted(commands)))

def create_response(message, bot_id):
  """Return a response to the message if it's about screambot.

  Args:
    message: (str) The entire line that someone typed. Slack sends these to us.
    bot_id: (str) Screambot's userid. It looks like "@U1234566"
  Returns:
    (str) A string to respond with or None.
  """
  # Only trigger on sentences containing "screambot" or @screambot's UID.
  if bot_id.lower() not in message.lower() and "screambot" not in message.lower():
    return

  # First handle commands starting with a username
  matches = re.search(COMMAND_REGEX, message)
  if matches:
    # Matches things like "@screambot scream a thing" and "@tanya some message" 
    user = matches.group(1)  # Who was mentioned, e.g., screambot or tanya
    if user != bot_id: # It was a message for someone else that included the word 'screambot'
      return "You're talking about me <3"

    command = matches.group(2).lower() # Everything past the name: "do a thing".

    # A complete command like "hug" or "freak out".
    if command in STANDALONE_COMMANDS:
      return STANDALONE_COMMANDS[command]

    # A single emoji, not counting any caught by the STANDALONE_COMMANDS.
    if re.match(":[\w_-]+:", command):
      return command + command + command + "!"

    # A command at the start of the line, like scream or hate. The template is
    # to replace "$what" with the rest of the line.
    for text in STARTER_COMMANDS.keys():
      if command.startswith(text.lower()):
        thing = command[len(text):] # Everything but the starter words
        string = Template(STARTER_COMMANDS[text]).safe_substitute(what=thing)
        if string.startswith("FUNCTION:UPPERCASE "):
          return string.lstrip("FUNCTION:UPPERCASE ").upper()
        if string.startswith("FUNCTION:HELP"):
          return help_message()
        return string

    # A command that contains a word that wasn't caught by the STARTER_COMMANDS.
    # The template is to replace "$what" with the entire command. 
    for text in CONTAIN_COMMANDS.keys():
      if text in command:
        template = Template(CONTAIN_COMMANDS[text])
        return template.safe_substitute(what=command)

    # A direct command we don't know how to handle.
    return "I don't know how to %s" % command
 
  # Now handle messages that don't start with @screambot, but use her name.
  for text in CONVERSATION.keys():
    if text in message.lower():
      template = Template(CONVERSATION[text])
      return template.safe_substitute(what=text)

  return "Want me to do something? Start your message with @screambot."

