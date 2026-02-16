#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import re
import string

# Global storage reference (set by app.py)
_storage = None

def set_storage(storage):
  """Set the storage manager (called from app.py)."""
  global _storage
  _storage = storage

COMMAND_REGEX = r"^<@([WU][^>]*)>[:,]? (.+)"
MAX_INPUT_LENGTH = 2000  # Slack's message limit

# It's a command to @screambot and this is the entire thing.
STANDALONE_COMMANDS = {
  "botsnack": ":cookie:",
  "cookie": ":cookie:",
  "celebrate": ":tada: :tada: :cake: :raised_hands: :raised_hands: :champagne: :doughnut: :sparkles: :sparkler: :tada: ",
  "cheer": ":sparkles: :raised_hands: :raised_hands: :tada: :tada: :sparkles:",
  "cry": "blooooohooohooohooo :sob:",
  "freak out": "*breathes into a paper bag*",
  "lose it": "I am kind of losing my shit right now?",
  "lose your shit": "FUUUUUUUUUUUUUUUUUUUUUUUCK",
  "scream": "AAAARRGGHHHHHHHHHHHHHH",
  "thank you": "Glad to help <3",
  "thanks": "Any time, friend.",
  "grimace": "oof :grimacing:",
  "hug": ":virtualhug:",
  "flip": "(╯°□°）╯︵ ┻━┻)",
  "tableflip": "(╯°□°）╯︵ ┻━┻)",
  ":heart:": ":heart:",
  "&lt;3": ":heart:",
  ":poop:": "Seriously.",
  "sigh": ":slightly_frowning_face:",
  "sob": "blooooohooohooohooo :sob:",
  "tea": "Always. :tea:",
  "whimper": "eep",
  "yo": "Yo.",
  ":yo:": "Yo.",
}

# It's a direct command to @screambot and it starts with this.
# "$what" will be replaced with the thing to scream about.
# TODO: Add "$who" and figure out how to talk to.

# Process multiword commands first to avoid partial matches
# (e.g., "lose it about" should match before "lose")
STARTER_COMMANDS_LONG = {
  "announce that ": ":star: :star: EXCUSE ME HI I HAVE AN ANNOUNCEMENT: $what :star: :star:",
  "freak out about ": "I am LOSING MY SHIT about $what right now.",
  "hate on ": "You know what I really hate? What I really hate is $what.",
  "rant about": "AUGH seriously though you know what sucks?? $what, that's what sucks.",
  "rant on": "AUGH seriously though you know what sucks?? $what, that's what sucks.",
  "lose it about ": "AGH what is GOING ON with $what? WHY is it LIKE THAT?",
  "lose your shit about ": "FUUUUUUUUUUUUCK I am NOT able to deal with $what AAARGGHHHH",
  "react to ": "EXCUSE ME HI we need to talk about $what. How's everyone feeling about that?",
  "save me from ": ":fire: pew :fire:pew :fire: I have exploded all the $what. :fire: You're welcome. :fire:",
  "sigh about ": "Yeah, $what is not the best, is it? :tea:?",
  "what can you ": lambda _: help_message(),
}

STARTER_COMMANDS = {
  "announce ": ":star: :star: EXCUSE ME HI I HAVE AN ANNOUNCEMENT: $what :star: :star:",
  "blame ": "Grr, $what strikes again.",
  "celebrate ": ":sparkles: :raised_hands: :raised_hands: hurray for $what!! :tada: :tada: :sparkles:",
  "cheer ": ":sparkles: :raised_hands: :raised_hands: hurray $what!! :tada: :tada: :sparkles:",
  # "destroy CITY" - destroys the specified city (also in CONTAIN_COMMANDS with different behavior)
  "destroy ": lambda city: rage(city=city),
  "flip": "(╯°□°）╯︵ ┻━┻)",
  "fuck ": "$what needs to fuck off right now :rage:",
  "hug ": ":virtualhug: for $what",
  "hate ": "I hate $what SO MUCH. Ugh, the worst.",
  "rant": "AUGH seriously though you know what sucks?? $what, that's what sucks.",
  "love ": "$what is pretty much the best thing.",
  "scream ": lambda what: what.upper(),
  "tableflip": "(╯°□°）╯︵ ┻━┻)",
  "help": lambda _: help_message(),
}

# Behave exactly as starter commands but aren't in the "what can you do" list.
# Easter eggs, I guess :-)
STARTER_COMMANDS_EE = {
  "you": "I promise to always try.",
  "is ": "I'm just a small bot making my way in the world.",
  "i love you": "It's mutual, I promise you.",
  "&lt;3": "Right back at you <3",
  "good bot": ":heart:",
  "hello": lambda _: hi(),
  "howdy": lambda _: hi(),
  "hi": lambda _: hi(),
  "what's up": lambda _: hi(),
  "hey": lambda _: hi(),
  "ello": lambda _: hi(),
}

# It's a direct command to @screambot and it contains this text.
CONTAIN_COMMANDS = {
  "ai": "I'm not an AI. I'm a maze of twisty if statements.",
  "birthday": ":birthday:",
  "botsnack": ":cookie:",
  "chatgpt": "I'm a little intimidated by ChatGPT to be honest. But glad of more bot friends.",
  "cookie": ":cookie:",
  "code": "My code's at https://github.com/whereistanya/screambot. Send Tanya a PR. :computer:",
  "github": "My code's at https://github.com/whereistanya/screambot. Send Tanya a PR. :computer:",
  "can you even": "I literally can't even.",
  "work": "WERK!",
  "industry": ":poop: :fire:",
  "patriarchy": lambda _: random_quote("feminism"),
  "feminism": lambda _: random_quote("feminism"),
  "tech": lambda _: random_quote("tech"),
  "inspire": lambda _: random_quote("tech"),
  "inspiration": lambda _: random_quote("tech"),
  "rage": lambda _: rage(city=None, rage_level=random.random()),
  # "...destroy..." - random city with random rage level (also in STARTER_COMMANDS with different behavior)
  "destroy": lambda _: rage(city=None, rage_level=random.random()),
  "&lt;3": ":heart:",
  "food": ":pizza:",
  "systemd": "systemd is strange and mysterious. Bring back init scripts!",
  "systemctl": "systemctl is strange and mysterious. Bring back init scripts!",
  "tea": "Always here for afternoontea :tea: :female-technologist:",
  "why": lambda _: why(),
}

# It's not a command but it contains the word screambot and this text.
CONVERSATION = {
  "birthday": ":birthday:",
  "botsnack": ":cookie:",
  "code": "My code's at https://github.com/whereistanya/screambot. Send Tanya a PR.",
  "github": "My code's at https://github.com/whereistanya/screambot. Send Tanya a PR.",
  "thank": "Any time.",
  ":heart:": ":heart_eyes:",
  "love": ":heart_eyes:",
  "good": ":heart_eyes:",
  "&lt;3": ":heart:",
  "sedgwick": "Don't get me started! Sedgwick's servers should all melt permanently. Preferably without backups.",
}

quotes = {
  "feminism": [
    """"I am deliberate and afraid of nothing." -- Audre Lorde""",
    """"Freedom cannot be achieved unless women have been emancipated from all forms of oppression" -- Nelson Mandela""",
    """"I've never been interested in being invisible and erased."-- Laverne Cox.""",
    """"Unlikeable women] accept the consequences of their choices, and those consequences become stories worth reading." -- Roxane Gay""",
    """"I want to be respected in all my femaleness. Because I deserve to be." -- Chimamanda Ngozi Adichie""",
    """"No woman can call herself free who does not own and control her own body" -- Margaret Sanger""",
    """"Nolite te bastardes carborundorum." -- Margaret Atwood""",
    """"There is no gate, no lock, no bolt that you can set upon the freedom of my mind." -- Virginia Woolf""",
    """"If one man can destroy everything, why can't one girl change it?" -- Malala Yousafzai""",
    """"Time is on the side of change." -- Ruth Bader Ginsberg""",
    """"Some people really feel uncomfortable around women who don't hate themselves. So that's why you need to be a little bit brave." -- Mindy Kaling""",
    """"We're all building our world, right now, in real time." -- Lindy West""",
    """"So use that anger. You write it. You paint it. You dance it. You march it. You vote it. You do everything about it. You talk it. Never stop talking it." -- Maya Angelou""",
    """"If we do not share our stories and shine a light on inequities, things will not change." -- Ellen Pao""",
    """"The difference between a broken community and a thriving one is the presence of women who are valued." --- Michelle Obama""",
    """"I'm tough, I'm ambitious, and I know exactly what I want. If that makes me a bitch, okay." --  Madonna""",
  ],

  "tech": [
    """"I also say to my team: Do 10% of your job shittily. It`s okay to do something shittily. Perfectionism prevents us from taking double steps in our career. We think we have to be perfect, but we don't" -- Reshma Saujani""",
    """"I am a big supporter of the minimum viable product and taking something that is the simplest explanation of your idea and putting it into the marketplace so you can start to get feedback." -- Kathryn Minshew""",
    """"Feeling a little uncomfortable with your skills is a sign of learning, and continuous learning is what the tech industry thrives on! It's important to seek out environments where you are supported, but where you have the chance to be uncomfortable and learn new things." -- Vanessa Hurst""",
    """"The world would be a better place if more engineers, like me, hated technology. The stuff I design, if I'm successful, nobody will ever notice." -- Radia Perlman""",
    """"Opportunities, the good ones, they're messy and confusing and hard to recognize. They're risky. They challenge you." -- Susan Wojcicki""",
  ]
}

cities = ["Beijing", "Berlin", "Cairo", "Dhaka", "Chicago", "Karachi", "Houston", "Istanbul", "Jakarta", "Johannesburg", "Kinshasa", "Lagos", "London", "Los Angeles", "Manila", "Moscow", "Mexico City", "Mumbai", "New york", "Paris", "Phoenix", "Seoul", "Shanghai", "Sao Paolo", "Shenzen", "Sydney", "Tianjin", "Tokyo",]

reasons = ["Like, if we understood that, we'd understand a lot of things",
           "I'm just a simple bot. These questions are too big for me.",
           "Because society, mostly?",
           "It's a surprisingly elaborate plot.",
           "Space weasels, pretty sure.",
           "It can probably be traced back to the French revolution.",
           "I'm not sure.",
           "I blame the parents.",
           "Because they killed Google Reader.",
           "It's a good question, and the answer is: I do not know.",
           "42",
           "I can answer everything... except that.",
           "I need to think about that. Ask me again tomorrow?",
           "I wish I knew.",
           ":woman-shrugging:",
           ":upside_down_face:",
           "I don't know but I bet someone in #random has an idea.",
          ]

greetings = ["Hi!", "Hi there!", "Hello!", "Hey there!", "Ello!"]

def rage(city=None, rage_level=1.0):
  """Destroys a major city."""
  if not city:
    city = random.choice(cities)
  s = ":t-rex: RARRRRR DESTROY %s :t-rex:" % city.upper()
  if rage_level < 0.2:
    s += " (*writes a sternly worded letter to their newspaper*)"
  return s

def why(testing=False):
    reason = random.choice(reasons)
    if testing:
        return "Nobody knows :-("
    return reason

def hi(testing=False):
    greeting = random.choice(greetings)
    if testing:
        return "Hi!"
    return greeting


def random_quote(key):
  """Returns a quote from the quotes dict."""
  if key in quotes:
    return random.choice(quotes[key])
  else:
    return random.choice(quotes["tech"])


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


def check_starters(command, starts):
  for text in starts.keys():
    if command.lower().startswith(text.lower()):
      thing = command[len(text):] # Everything but the starter words
      value = starts[text.lower()]

      # Check if it's callable (function/lambda)
      if callable(value):
        return value(thing)
      else:
        # It's a string template
        return string.Template(value).safe_substitute(what=thing)
  return None  # No match found


def _should_respond(message, bot_id):
  """Check if screambot should respond to this message."""
  return bot_id.lower() in message.lower() or "screambot" in message.lower()


def _parse_message(message, bot_id):
  """Parse a message to extract the command and whether it's a direct command.

  Returns:
    Tuple of (command, is_direct) where command is the extracted text or None,
    and is_direct indicates if this is a direct command to screambot.
  """
  # First handle commands starting with a username like <@WABC123>.
  matches = re.search(COMMAND_REGEX, message)
  if matches:
    user = matches.group(1)
    if user != bot_id:
      return (None, False)
    command = matches.group(2).lower().lstrip()
    return (command, True)

  # Handle commands containing "screambot" or "@screambot" anywhere in the message.
  # Extract everything after the word "screambot" as the command.
  message_lower = message.lower()
  for trigger in ["@screambot", "screambot"]:
    if trigger in message_lower:
      # Find the position of "screambot" in the message
      pos = message_lower.find(trigger)
      # Extract everything after "screambot"
      after_trigger = message[pos + len(trigger):].lstrip()

      # Remove leading punctuation like "," or ":" or "?"
      after_trigger = after_trigger.lstrip(':,?!.').lstrip()

      # If "screambot" is at the start, always treat as direct (even with no command)
      if pos == 0:
        return (after_trigger if after_trigger else None, True)

      # If "screambot" is in the middle, only treat as direct if there's a command after it
      if after_trigger:
        return (after_trigger, True)
      else:
        # No command after "screambot" in the middle - conversation mention
        return (None, False)

  return (None, False)


def _handle_direct_command(command, speaker, user_id=None):
  """Handle a direct command to screambot."""
  # Validate input length to prevent memory exhaustion
  if len(command) > MAX_INPUT_LENGTH:
    return "That's too much for me to handle!"

  # Check for "custom" command - triggers Slack UI
  if command.lower() == "custom":
    return "__OPEN_MANAGE_COMMANDS_UI__"

  # Check custom commands FIRST (before built-in commands)
  if _storage and user_id:
    # Get all custom commands
    all_custom_commands = _storage.list_all_commands()

    # First, try exact matches
    for cmd in all_custom_commands:
      if command.lower() == cmd['trigger']:
        return cmd['response']

    # Second, try prefix matches (for templates)
    for cmd in all_custom_commands:
      trigger = cmd['trigger']
      # Check if command starts with trigger and has non-whitespace after it
      if command.lower().startswith(trigger):
        remainder = command[len(trigger):].lstrip()
        if remainder:  # There's non-whitespace text after the trigger
          # Extract the "what" part and substitute
          return string.Template(cmd['response']).safe_substitute(what=remainder)

  # A complete command like "hug" or "freak out".
  if command in STANDALONE_COMMANDS:
    return STANDALONE_COMMANDS[command]

  # Try with stripped punctuation.
  remove_punctuation = str.maketrans('', '', string.punctuation)
  stripped = command.translate(remove_punctuation)
  if stripped in STANDALONE_COMMANDS:
    return STANDALONE_COMMANDS[stripped]

  # A single emoji.
  if re.match(":[\w_-]+:", command):
    return command + command + command + "!"

  # Starter commands.
  for command_set in [STARTER_COMMANDS_LONG, STARTER_COMMANDS_EE, STARTER_COMMANDS]:
    response = check_starters(command, command_set)
    if response:
      return response

  # Contain commands.
  for text in CONTAIN_COMMANDS.keys():
    if text.lower() in command.lower():
      value = CONTAIN_COMMANDS[text.lower()]
      if callable(value):
        return value(command.lower())
      else:
        return string.Template(value).safe_substitute(what=command.lower())

  # Unknown command.
  return ("Sorry, %s, I don't know how to %s yet. You can tell me how by typing "
          "`screambot custom`. Feel free to DM me if you prefer to try it out in a DM "
          "instead of in a channel." % (speaker, command))


def _check_conversation(message):
  """Handle passive mentions of screambot (not direct commands)."""
  for text in CONVERSATION.keys():
    if text.lower() in message.lower():
      value = CONVERSATION[text.lower()]
      if callable(value):
        return value(text.lower())
      else:
        return string.Template(value).safe_substitute(what=text.lower())
  return None


def create_response(message, bot_id, speaker=None, user_id=None):
  """Return a response to the message if it's about screambot.

  Args:
    message: (str) The entire line that someone typed. Slack sends these to us.
    bot_id: (str) Screambot's userid. It looks like "@U1234566"
    speaker: (str) The name of the person who invoked screambot.
    user_id: (str) The Slack user ID of the person (for custom commands).
  Returns:
    (str) A string to respond with or None.
  """
  # Only trigger on sentences containing "screambot" or @screambot's UID.
  if not _should_respond(message, bot_id):
    return None

  # Parse the message to extract command and determine if it's direct.
  command, is_direct = _parse_message(message, bot_id)

  # Handle direct commands to screambot.
  if is_direct:
    if command:
      return _handle_direct_command(command, speaker, user_id)
    else:
      return "Want me to do something, %s? Start your message with @screambot." % speaker

  # Handle passive mentions (someone mentioned screambot but it wasn't directed at us).
  response = _check_conversation(message)
  if response:
    return response

  # Someone mentioned us in a message to someone else.
  return "You're talking about me <3"

