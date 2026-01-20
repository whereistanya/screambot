#!/usr/bin/env python3

# Run the tests with
# python3 -m pytest

import unittest
import responses

class TestScreambot(unittest.TestCase):

  def test_response(self):
    bot_id = "UA1234567"
    cases = {
      "<@UA1234567> hug": ":virtualhug:",
      "<@UA1234567> hug!": ":virtualhug:",
      "<@UA1234567> scream?": "AAAARRGGHHHHHHHHHHHHHH",
      "<@UA1234567> scream??!?!?!": "AAAARRGGHHHHHHHHHHHHHH",
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
      "@screambot yo": "Yo.",
      "@Screambot yo": "Yo.",
      "Screambot, yo": "Yo.",
      "Screambot     yo": "Yo.",
      "Screambot hate on mosquitoes": "You know what I really hate? What I really hate is mosquitoes.",
      "does screambot want a botsnack?": ":cookie:",
      "thanks, @screambot": "Any time.",
      "good work, screambot": ":heart_eyes:",
      "&lt;3 screambot": ":heart:",
      "<@UA1234567> someunknownthing": "Sorry, some_user, I don't know how to someunknownthing",
    }

    for message, expected in cases.items():
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

      expected = ":t-rex: RARRRRR DESTROY CITY :t-rex: (*writes a sternly worded letter to their newspaper*)"
      got = responses.rage("CITY", 0.1)
      self.assertEqual(expected, got)

  def test_input_length_validation(self):
      bot_id = "UA1234567"
      # Test with command just under the limit (2000 chars total, "scream " is 7 chars)
      long_input = "A" * 1993
      response = responses.create_response(f"screambot scream {long_input}", bot_id)
      self.assertEqual(response, long_input.upper())

      # Test with command over the limit
      too_long = "A" * 1994
      response = responses.create_response(f"screambot scream {too_long}", bot_id)
      self.assertEqual(response, "That's too much for me to handle!")

class TestHelperFunctions(unittest.TestCase):
  """Test the helper functions extracted during refactoring."""

  def test_should_respond_with_bot_id(self):
    self.assertTrue(responses._should_respond("hi <@U123>", "U123"))
    self.assertTrue(responses._should_respond("hello <@U123> there", "U123"))

  def test_should_respond_with_screambot_name(self):
    self.assertTrue(responses._should_respond("hi screambot", "U123"))
    self.assertTrue(responses._should_respond("hey Screambot!", "U123"))

  def test_should_not_respond(self):
    self.assertFalse(responses._should_respond("hello world", "U123"))
    self.assertFalse(responses._should_respond("", "U123"))

  def test_parse_message_with_screambot_prefix(self):
    command, is_direct = responses._parse_message("screambot yo", "U123")
    self.assertEqual(command, "yo")
    self.assertTrue(is_direct)

  def test_parse_message_with_at_screambot_prefix(self):
    command, is_direct = responses._parse_message("@screambot yo", "U123")
    self.assertEqual(command, "yo")
    self.assertTrue(is_direct)

  def test_parse_message_with_bot_id(self):
    command, is_direct = responses._parse_message("<@U123> scream hello", "U123")
    self.assertEqual(command, "scream hello")
    self.assertTrue(is_direct)

  def test_parse_message_empty_command(self):
    command, is_direct = responses._parse_message("screambot", "U123")
    self.assertIsNone(command)
    self.assertTrue(is_direct)

  def test_parse_message_different_user(self):
    command, is_direct = responses._parse_message("<@U456> hello", "U123")
    self.assertIsNone(command)
    self.assertFalse(is_direct)

  def test_parse_message_not_direct(self):
    command, is_direct = responses._parse_message("I love screambot", "U123")
    self.assertIsNone(command)
    self.assertFalse(is_direct)

  def test_check_starters_with_template(self):
    starts = {"hate ": "I hate $what SO MUCH."}
    result = responses.check_starters("hate mondays", starts)
    self.assertEqual(result, "I hate mondays SO MUCH.")

  def test_check_starters_with_callable(self):
    starts = {"upper ": lambda what: what.upper()}
    result = responses.check_starters("upper hello", starts)
    self.assertEqual(result, "HELLO")

  def test_check_starters_no_match(self):
    starts = {"hate ": "I hate $what"}
    result = responses.check_starters("love mondays", starts)
    self.assertIsNone(result)

  def test_check_conversation(self):
    result = responses._check_conversation("does screambot want a botsnack?")
    self.assertEqual(result, ":cookie:")

  def test_check_conversation_no_match(self):
    result = responses._check_conversation("hello world")
    self.assertIsNone(result)


class TestLambdaCommands(unittest.TestCase):
  """Test commands that use callable lambdas instead of string templates."""

  def test_scream_uppercase(self):
    bot_id = "UA1234567"
    response = responses.create_response("screambot scream hello world", bot_id)
    self.assertEqual(response, "HELLO WORLD")

  def test_destroy_with_city(self):
    bot_id = "UA1234567"
    response = responses.create_response("screambot destroy Tokyo", bot_id)
    self.assertIn("TOKYO", response)
    self.assertIn(":t-rex:", response)

  def test_help_lambda(self):
    bot_id = "UA1234567"
    response = responses.create_response("screambot help", bot_id)
    self.assertIn("Hi, I'm Screambot", response)
    self.assertIn("Commands:", response)

  def test_what_can_you_lambda(self):
    bot_id = "UA1234567"
    response = responses.create_response("screambot what can you do?", bot_id)
    self.assertIn("Hi, I'm Screambot", response)

  def test_hi_lambdas(self):
    bot_id = "UA1234567"
    # Test one of the greeting lambdas
    response = responses.create_response("screambot hello", bot_id)
    self.assertIn(response, responses.greetings)

  def test_random_quote_lambda(self):
    bot_id = "UA1234567"
    response = responses.create_response("screambot tell me about feminism", bot_id)
    self.assertIn(response, responses.quotes["feminism"])

  def test_why_lambda(self):
    bot_id = "UA1234567"
    response = responses.create_response("screambot why is this happening", bot_id)
    self.assertIn(response, responses.reasons)

  def test_contain_destroy_lambda(self):
    bot_id = "UA1234567"
    # This uses CONTAIN_COMMANDS which has random rage level
    response = responses.create_response("screambot can you destroy it", bot_id)
    self.assertIn(":t-rex:", response)
    self.assertIn("RARRRRR DESTROY", response)


class TestEdgeCases(unittest.TestCase):
  """Test edge cases and unusual inputs."""

  def test_empty_message(self):
    bot_id = "UA1234567"
    response = responses.create_response("", bot_id)
    self.assertIsNone(response)

  def test_only_whitespace(self):
    bot_id = "UA1234567"
    response = responses.create_response("   ", bot_id)
    self.assertIsNone(response)

  def test_only_whitespace_after_command(self):
    bot_id = "UA1234567"
    response = responses.create_response("screambot    ", bot_id, "user")
    self.assertIn("Want me to do something", response)

  def test_unicode_input(self):
    bot_id = "UA1234567"
    response = responses.create_response("screambot scream 你好 🎉", bot_id)
    self.assertEqual(response, "你好 🎉")

  def test_special_characters(self):
    bot_id = "UA1234567"
    response = responses.create_response("screambot scream <script>alert('xss')</script>", bot_id)
    self.assertEqual(response, "<SCRIPT>ALERT('XSS')</SCRIPT>")

  def test_html_entities(self):
    bot_id = "UA1234567"
    # The &lt;3 gets converted to <3 in Slack
    response = responses.create_response("screambot &lt;3", bot_id)
    self.assertEqual(response, ":heart:")

  def test_multiple_spaces_in_command(self):
    bot_id = "UA1234567"
    # Multiple spaces get lstripped, then "scream " matches, leaving "  hello"
    response = responses.create_response("screambot   scream   hello", bot_id)
    self.assertEqual(response, "  HELLO")

  def test_case_insensitive_screambot(self):
    bot_id = "UA1234567"
    response = responses.create_response("ScReAmBoT yo", bot_id)
    self.assertEqual(response, "Yo.")

  def test_newlines_in_message(self):
    bot_id = "UA1234567"
    response = responses.create_response("screambot scream hello\nworld", bot_id)
    self.assertEqual(response, "HELLO\nWORLD")

  def test_very_long_city_name(self):
    bot_id = "UA1234567"
    long_city = "A" * 100
    response = responses.create_response(f"screambot destroy {long_city}", bot_id)
    self.assertIn(long_city.upper(), response)


if __name__ == 'main__':
    unittest.main()
