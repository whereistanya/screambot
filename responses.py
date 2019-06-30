#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import re
from string import Template

COMMAND_REGEX = "^<@(|[WU].+?)>[:,]? (.+)"

# It's a command to @screambot and this is the entire thing.
STANDALONE_COMMANDS = {
  "botsnack": ":cookie:",
  "celebrate": ":tada: :tada: :cake: :raised_hands: :raised_hands: :champagne: :doughnut: :sparkles: :sparkler: :tada: ",
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
  "whimper": "eep",
  "yo": "Yo.",
  ":yo:": "Yo.",
}

# It's a direct command to @screambot and it starts with this.
# "$what" will be replaced with the thing to scream about.
# TODO: Add "$who" and figure out how to talk to.
STARTER_COMMANDS = {
  "announce that ": ":star: :star: EXCUSE ME HI I HAVE AN ANNOUNCEMENT: $what :star: :star:",
  "announce ": ":star: :star: EXCUSE ME HI I HAVE AN ANNOUNCEMENT: $what :star: :star:",
  "blame ": "Grr, $what strikes again.",
  "celebrate ": ":sparkles: :raised_hands: :raised_hands: hurray for $what!! :tada: :tada: :sparkles:",
  "destroy ": "FUNCTION:RAGE $what",
  "flip ": "╯°□°）╯︵ ┻━�",
  "freak out about ": "I am LOSING MY SHIT about $what right now.",
  "fuck ": "$what needs to fuck off right now :rage:",
  "hug ": ":virtualhug: for $what",
  "hate ": "I hate $what SO MUCH. Ugh, the worst.",
  "hate on ": "You know what I really hate? What I really hate is $what.",
  "lose it about ": "AGH what is the deal with $what?",
  "lose your shit about ": "OH SHIT did you know about $what?",
  "love ": "$what is pretty much the best thing.",
  "react to ": "EXCUSE ME HI I have opinions about $what",
  "save me from ": ":fire: pew :fire:pew :fire: I have exploded all the $what. :fire: You're welcome. :fire:",
  "scream ": "FUNCTION:UPPERCASE $what",
  "sigh about ": "Yeah, $what is not the best, is it?",
  "tableflip ": "╯°□°）╯︵ ┻━�",
  "help": "FUNCTION:HELP",
  "what can you ": "FUNCTION:HELP",
}

# Behave exactly as starter commands but aren't in the "what can you do" list.
# Easter eggs, I guess :-)
STARTER_COMMANDS_EE = {
  "you": "I promise to always try.",
  "is ": "I'm just a small bot making my way in the world.",
  "I love you": "It's mutual, I promise you.",
  "&lt;3": "Right back at you <3",
  "why ": "I'm a simple bot. It is not for me to speculate.",
  "good bot": ":heart:",
}

# It's a direct command to @screambot and it contains this text.
CONTAIN_COMMANDS = {
  "birthday": ":birthday:",
  "botsnack": ":cookie:",
  "code": "My code's at https://github.com/whereistanya/screambot. Send Tanya a PR. :computer:",
  "github": "My code's at https://github.com/whereistanya/screambot. Send Tanya a PR. :computer:",
  "can you even": "I literally can't even.",
  "work": "WERK!",
  "industry": ":poop: :fire:",
  "patriarchy": "FUNCTION:RANDOM feminism",
  "feminism": "FUNCTION:RANDOM feminism",
  "tech": "FUNCTION:RANDOM tech",
  "inspire": "FUNCTION:RANDOM tech",
  "inspiration": "FUNCTION:RANDOM tech",
  "rage": "FUNCTION:RAGE",
  "destroy": "FUNCTION:RAGE",
  "&lt;3": ":heart:",
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

def rage(city=None, rage_level=1.0):
  """Destroys a major city."""
  if not city:
    city = random.choice(cities)
  s = ":t-rex: RARRRRR DESTROY %s :t-rex:" % city.upper()
  if rage_level < 0.2:
    s += " (*writes a sternly worded letter to their newspaper*)"
  return s

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

  user = None
  command = None
  # First handle commands starting with "screambot" or "Screambot:" or similar. Not
  # "@screambot" though. That comes next.
  if message.lower().startswith("screambot"):
    user = "screambot"
    command = message.split(' ', 1)[1].lstrip()  # everything but the first word.
  # Next try things starting with a username, which we get as an internal uid like <@WABC123>.
  else:
    matches = re.search(COMMAND_REGEX, message)
    if matches:
    # Matches things like "@screambot scream a thing" and "@tanya some message"
      user = matches.group(1)  # Who was mentioned, e.g., screambot or tanya
      if user != bot_id: # It was a message for someone else that included the word 'screambot'
        return "You're talking about me <3"
      command = matches.group(2).lower().lstrip()  # Everything past the name: "do a thing".

  if user and command:
    # A complete command like "hug" or "freak out".
    if command in STANDALONE_COMMANDS:
      return STANDALONE_COMMANDS[command]

    # A single emoji, not counting any caught by the STANDALONE_COMMANDS.
    if re.match(":[\w_-]+:", command):
      return command + command + command + "!"

    # A command at the start of the line, like scream or hate. We maintain two
    # dictionaries: the ones we want to show up in the help message and cute
    # surprise extras. We combine them here.
    starts = STARTER_COMMANDS.copy()
    starts.update(STARTER_COMMANDS_EE.copy())

    for text in starts.keys():
      if command.startswith(text.lower()):
        thing = command[len(text):] # Everything but the starter words
        # The template replaces "$what" with the rest of the line.
        string = Template(starts[text]).safe_substitute(what=thing)
        if string.startswith("FUNCTION:UPPERCASE "):
          stripped = string[len("FUNCTION:UPPERCASE "):]
          return stripped.upper()
        if string.startswith("FUNCTION:HELP"):
          return help_message()
        if string.startswith("FUNCTION:RANDOM "):
          stripped = string[len("FUNCTION:RANDOM "):]
          return random_quote(stripped)
        if string.startswith("FUNCTION:RAGE "):
          stripped = string[len("FUNCTION:RAGE "):]
          return rage(city=stripped)
        return string

    # A command that contains a word that wasn't caught by the STARTER_COMMANDS.
    # The template is to replace "$what" with the entire command.
    for text in CONTAIN_COMMANDS.keys():
      if text in command:
        template = Template(CONTAIN_COMMANDS[text])
        string = template.safe_substitute(what=command)
        if string.startswith("FUNCTION:RANDOM "):
          stripped = string[len("FUNCTION:RANDOM "):]
          return random_quote(stripped)
        if string.startswith("FUNCTION:RAGE"):
          rage_level = random.random()
          return rage(city=None, rage_level=rage_level)
        return string

    # A direct command we don't know how to handle.
    return "I don't know how to %s" % command
 
  # Now handle messages that don't start with @screambot/screambot, but use
  # her name somewhere in the sentence.
  for text in CONVERSATION.keys():
    if text in message.lower():
      template = Template(CONVERSATION[text])
      string = template.safe_substitute(what=text)
      if string.startswith("FUNCTION:RANDOM "):
        stripped = string[len("FUNCTION:RANDOM "):]
        return random_quote(stripped)
      return string

  return "Want me to do something? Start your message with @screambot."

