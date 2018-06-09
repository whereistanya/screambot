#!/usr/bin/env python

import unittest
import responses

class TestScreambot(unittest.TestCase):

  def test_response(self):

    bot_id = "UA1234567"
    cases = {
      "<@UA1234567> hug": ":virtualhug:",
      "<@UA1234567> hug a cat": ":virtualhug: for a cat",
      "<@UA1234567> :love:": ":love::love::love:!",
      "<@UA1234567> can you even believe it:": "I literally can't even.",
      "<@UA1234567> lose it about pocketless dresses": "AGH what is the deal with pocketless dresses?",
      "<@UA1234567> hate spam calls": "I hate spam calls SO MUCH. Ugh, the worst.",
      "<@UA1234567> scream the scream code is a hack, Tanya.": "THE SCREAM CODE IS A HACK, TANYA.",
      "<@UA1234567> scream something": "SOMETHING",
      "screambot scream something": "SOMETHING",
      "screambot scream I love cats": "I LOVE CATS",
      "<@UA1234567> scream <system> is broken": "<SYSTEM> IS BROKEN",
      "<@UA1234567> I love you, screambot": "It's mutual, I promise you.",
      "<@UAXXXXXXX> what is screambot?": "You're talking about me <3",
      "<@UA1234567> blame systemd": "Grr, systemd strikes again.",
      "screambot blame the rain": "Grr, the rain strikes again.",
      "Screambot yo": "Yo.",
      "does screambot want a botsnack?": ":cookie:",
      "thanks, @screambot": "Any time.",
      "good work, screambot": ":heart_eyes:",
    }

    for message, expected in cases.iteritems():
      response = responses.create_response(message, bot_id)
      self.assertEqual(response, expected)

  def test_help(self):
    bot_id = "UA1234567"
    cases = [
      "<@UA1234567> help",
      "<@UA1234567> what can you do?",
    ]
    for case in cases:
      response = responses.create_response(case, bot_id)
      self.assertTrue("scream;" in response)
      self.assertTrue("Hi, I'm Screambot" in response)

  def test_random(self):
    bot_id = "UA1234567"
    case = "screambot how about that patriarchy"
    response = responses.create_response(case, bot_id)
    quotes = responses.quotes["feminism"]
    self.assertTrue(response in quotes)

if __name__ == 'main__':
    unittest.main()
