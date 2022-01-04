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
      "<@UA1234567>: :cat:": ":cat::cat::cat:!",
      "<@UA1234567> can you even believe it:": "I literally can't even.",
      "<@UA1234567> lose it about pocketless dresses": "AGH what is GOING ON with pocketless dresses? WHY is it LIKE THAT?",
      "<@UA1234567> hate spam calls": "I hate spam calls SO MUCH. Ugh, the worst.",
      "<@UA1234567>  hate double whitespace": "I hate double whitespace SO MUCH. Ugh, the worst.",
      "<@UA1234567> scream the scream code is a hack, Tanya.": "THE SCREAM CODE IS A HACK, TANYA.",
      "<@UA1234567> scream something": "SOMETHING",
      "<@UA1234567>, scream I know about commas now": "I KNOW ABOUT COMMAS NOW",
      "screambot scream something": "SOMETHING",
      "screambot scream I love cats": "I LOVE CATS",
      "<@UA1234567> scream <system> is broken": "<SYSTEM> IS BROKEN",
      "<@UA1234567> I love you, screambot": "It's mutual, I promise you.",
      "<@UA1234567> i love you, screambot": "It's mutual, I promise you.",
      "<@UAXXXXXXX> what is screambot?": "You're talking about me <3",
      "<@UA1234567> blame systemd": "Grr, systemd strikes again.",
      "<@UA1234567> destroy Mountain View": ":t-rex: RARRRRR DESTROY MOUNTAIN VIEW :t-rex:",
      "screambot blame the rain": "Grr, the rain strikes again.",
      "Screambot yo": "Yo.",
      "Screambot, yo": "Yo.",
      "Screambot     yo": "Yo.",
      "Screambot hate on mosquitoes": "You know what I really hate? What I really hate is mosquitoes.",
      "does screambot want a botsnack?": ":cookie:",
      "thanks, @screambot": "Any time.",
      "good work, screambot": ":heart_eyes:",
      "&lt;3 screambot": ":heart:",
      "<@UA1234567> someunknownthing": "Sorry, some_user, I don't know how to someunknownthing",
    }

    for message, expected in cases.iteritems():
      response = responses.create_response(message, bot_id, "some_user")
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

  def test_why(self):
      self.assertEqual(responses.why(testing=True), "Nobody knows :-(")

  def test_rage(self):
      expected = ":t-rex: RARRRRR DESTROY CITY :t-rex:"
      got = responses.rage("CITY")
      self.assertEqual(expected, got)

      expected = ":t-rex: RARRRRR DESTROY CITY :t-rex:"
      got = responses.rage("CITY", 0.9)
      self.assertEqual(expected, got)

      expected = ":t-rex: RARRRRR DESTROY CITY :t-rex: (*writes sternly worded letter*)"
      got = responses.rage("CITY", 0.1)
      self.assertTrue(expected, got)

if __name__ == 'main__':
    unittest.main()
