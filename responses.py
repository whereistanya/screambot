#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import re
import string

COMMAND_REGEX = "^<@(|[WU].+?)>[:,]? (.+)"

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

# Do multiword commands first. This is shite and I should rewrite this whole
# thing some time.
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
  "what can you ": "FUNCTION:HELP",
}

STARTER_COMMANDS = {
  "announce ": ":star: :star: EXCUSE ME HI I HAVE AN ANNOUNCEMENT: $what :star: :star:",
  "blame ": "Grr, $what strikes again.",
  "celebrate ": ":sparkles: :raised_hands: :raised_hands: hurray for $what!! :tada: :tada: :sparkles:",
  "cheer ": ":sparkles: :raised_hands: :raised_hands: hurray $what!! :tada: :tada: :sparkles:",
  "destroy ": "FUNCTION:RAGE $what",
  "flip": "(╯°□°）╯︵ ┻━┻)",
  "fuck ": "$what needs to fuck off right now :rage:",
  "hug ": ":virtualhug: for $what",
  "hate ": "I hate $what SO MUCH. Ugh, the worst.",
  "rant": "AUGH seriously though you know what sucks?? $what, that's what sucks.",
  "love ": "$what is pretty much the best thing.",
  "scream ": "FUNCTION:UPPERCASE $what",
  "tableflip": "(╯°□°）╯︵ ┻━┻)",
  "help": "FUNCTION:HELP",
}

# Behave exactly as starter commands but aren't in the "what can you do" list.
# Easter eggs, I guess :-)
STARTER_COMMANDS_EE = {
  "you": "I promise to always try.",
  "is ": "I'm just a small bot making my way in the world.",
  "i love you": "It's mutual, I promise you.",
  "&lt;3": "Right back at you <3",
  "good bot": ":heart:",
  "hello": "FUNCTION:HI",
  "howdy": "FUNCTION:HI",
  "hi": "FUNCTION:HI",
  "what's up": "FUNCTION:HI",
  "hey": "FUNCTION:HI",
  "ello": "FUNCTION:HI",
}

# It's a direct command to @screambot and it contains this text.
CONTAIN_COMMANDS = {
  "birthday": ":birthday:",
  "botsnack": ":cookie:",
  "chatgpt": "I'm a little intimidated by ChatGPT to be honest. But glad of more bot friends.",
  "cookie": ":cookie:",
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
  "food": ":pizza:",
  "systemd": "systemd is strange and mysterious. Bring back init scripts!",
  "systemctl": "systemctl is strange and mysterious. Bring back init scripts!",
  "tea": "Always here for afternoontea :tea: :female-technologist:",
  "why": "FUNCTION:WHY",
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
      # The template replaces "$what" with the rest of the line.
      command = string.Template(starts[text.lower()]).safe_substitute(what=thing)
      if command.startswith("FUNCTION:UPPERCASE "):
        stripped = command[len("FUNCTION:UPPERCASE "):]
        return stripped.upper()
      if command.startswith("FUNCTION:HELP"):
        return help_message()
      if command.startswith("FUNCTION:RANDOM "):
        stripped = command[len("FUNCTION:RANDOM "):]
        return random_quote(stripped)
      if command.startswith("FUNCTION:RAGE "):
        stripped = command[len("FUNCTION:RAGE "):]
        return rage(city=stripped)
      if command.startswith("FUNCTION:HI"):
        return hi()
      return command


def create_response(message, bot_id, speaker=None):
  """Return a response to the message if it's about screambot.

  Args:
    message: (str) The entire line that someone typed. Slack sends these to us.
    bot_id: (str) Screambot's userid. It looks like "@U1234566"
    speaker: (str) The name of the person who invoked screambot.
  Returns:
    (str) A string to respond with or None.
  """
  # Only trigger on sentences containing "screambot" or @screambot's UID.
  if bot_id.lower() not in message.lower() and "screambot" not in message.lower():
    return

  user = None
  command = None
  # First handle commands starting with "screambot" or "Screambot:" or similar.
  # Usually the text '@screambot' gets translated into an id instead, but
  # occasionally slack sends us the word instead, so we check for that too.
  if message.lower().startswith("screambot") or message.lower().startswith("@screambot"):
    user = "screambot"
    try:
        command = message.split(' ', 1)[1].lstrip()  # everything but the first word.
    except IndexError:
        command = None

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

    # Try the same thing again with stripped punctuation. Some commands can
    # contain punctuation, like the very important '<3' command, so we try it
    # first as-is, then have a second attempt so we can catch things like "scream!"
    remove_punctuation = str.maketrans('', '', string.punctuation)
    stripped = command.translate(remove_punctuation)
    if stripped in STANDALONE_COMMANDS:
      return STANDALONE_COMMANDS[stripped]

    # A single emoji, not counting any caught by the STANDALONE_COMMANDS.
    if re.match(":[\w_-]+:", command):
      return command + command + command + "!"

    # A command at the start of the line, like scream or hate. We maintain three
    # dictionaries:
    # STARTER_COMMANDS_LONG: multiword commands that we want to match first
    # STARTER_COMMANDS: one word commands
    # STARTER_COMMANDS_EE: easter eggs that don't show up in the help message,
    # just for fun
    for command_set in [STARTER_COMMANDS_LONG, STARTER_COMMANDS_EE,
                         STARTER_COMMANDS]:
      response = check_starters(command, command_set)
      if response:
        return response

    # A command that contains a word that wasn't caught by the STARTER_COMMANDS.
    # The template is to replace "$what" with the entire command.
    for text in CONTAIN_COMMANDS.keys():
      if text.lower() in command.lower():
        template = string.Template(CONTAIN_COMMANDS[text.lower()])
        command = template.safe_substitute(what=command.lower())
        if command.startswith("FUNCTION:RANDOM "):
          stripped = command[len("FUNCTION:RANDOM "):]
          return random_quote(stripped)
        if command.startswith("FUNCTION:RAGE"):
          rage_level = random.random()
          return rage(city=None, rage_level=rage_level)
        if command.startswith("FUNCTION:WHY"):
          stripped = command[len("FUNCTION:WHY"):]
          return why()
        return command

    # A direct command we don't know how to handle.
    return "Sorry, %s, I don't know how to %s" % (speaker, command)

  # Now handle messages that don't start with @screambot/screambot, but use
  # her name somewhere in the sentence.
  for text in CONVERSATION.keys():
    if text.lower() in message.lower():
      template = string.Template(CONVERSATION[text.lower()])
      command = template.safe_substitute(what=text.lower())
      if command.startswith("FUNCTION:RANDOM "):
        stripped = command[len("FUNCTION:RANDOM "):]
        return random_quote(stripped)
      return command

  return "Want me to do something, %s? Start your message with @screambot." % speaker

