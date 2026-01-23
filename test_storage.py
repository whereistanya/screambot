#!/usr/bin/env python3

import unittest
import os
from storage import StorageManager

class TestStorageManager(unittest.TestCase):

  def setUp(self):
    """Create a fresh test database for each test."""
    self.test_db = "test_screambot.db"
    if os.path.exists(self.test_db):
      os.remove(self.test_db)
    self.storage = StorageManager(self.test_db)

  def tearDown(self):
    """Clean up test database."""
    self.storage.close()
    if os.path.exists(self.test_db):
      os.remove(self.test_db)

  def test_add_command(self):
    result = self.storage.add_command("panic", "take a breath", "U123")
    self.assertTrue(result)

    response = self.storage.get_command("panic")
    self.assertEqual(response, "take a breath")

  def test_add_command_case_insensitive(self):
    self.storage.add_command("PANIC", "breathe", "U123")

    # Should match regardless of case
    response = self.storage.get_command("panic")
    self.assertEqual(response, "breathe")

    response2 = self.storage.get_command("PaNiC")
    self.assertEqual(response2, "breathe")

  def test_update_command(self):
    self.storage.add_command("panic", "breathe", "U123")
    self.storage.add_command("panic", "take a breath", "U456")

    response = self.storage.get_command("panic")
    self.assertEqual(response, "take a breath")

    # Should only have one command (not duplicated)
    commands = self.storage.list_all_commands()
    self.assertEqual(len(commands), 1)

  def test_get_nonexistent_command(self):
    response = self.storage.get_command("nonexistent")
    self.assertIsNone(response)

  def test_list_commands_empty(self):
    commands = self.storage.list_all_commands()
    self.assertEqual(len(commands), 0)

  def test_list_commands(self):
    self.storage.add_command("panic", "breathe", "U123")
    self.storage.add_command("focus", "you got this", "U456")

    commands = self.storage.list_all_commands()
    self.assertEqual(len(commands), 2)

    triggers = [cmd['trigger'] for cmd in commands]
    self.assertIn("panic", triggers)
    self.assertIn("focus", triggers)

  def test_list_commands_includes_metadata(self):
    self.storage.add_command("panic", "breathe", "U123")

    commands = self.storage.list_all_commands()
    self.assertEqual(len(commands), 1)

    cmd = commands[0]
    self.assertEqual(cmd['trigger'], "panic")
    self.assertEqual(cmd['response'], "breathe")
    self.assertEqual(cmd['created_by'], "U123")
    self.assertIn('created_at', cmd)

  def test_delete_command(self):
    self.storage.add_command("panic", "breathe", "U123")

    result = self.storage.delete_command("panic", "U456")
    self.assertTrue(result)

    response = self.storage.get_command("panic")
    self.assertIsNone(response)

  def test_delete_nonexistent_command(self):
    result = self.storage.delete_command("nonexistent", "U123")
    self.assertFalse(result)

  def test_get_command_creator(self):
    self.storage.add_command("panic", "breathe", "U123")

    creator = self.storage.get_command_creator("panic")
    self.assertEqual(creator, "U123")

  def test_get_creator_nonexistent(self):
    creator = self.storage.get_command_creator("nonexistent")
    self.assertIsNone(creator)

  def test_workspace_wide(self):
    """Test that commands work for all users."""
    # User U123 creates a command
    self.storage.add_command("panic", "breathe", "U123")

    # User U456 should be able to trigger it
    response = self.storage.get_command("panic")
    self.assertEqual(response, "breathe")

  def test_audit_log_create(self):
    """Test that creating a command logs to audit."""
    self.storage.add_command("panic", "breathe", "U123")

    audit = self.storage.get_audit_log(limit=10)
    self.assertEqual(len(audit), 1)

    entry = audit[0]
    self.assertEqual(entry['action'], "create")
    self.assertEqual(entry['trigger'], "panic")
    self.assertEqual(entry['response'], "breathe")
    self.assertEqual(entry['user_id'], "U123")
    self.assertIn('timestamp', entry)

  def test_audit_log_update(self):
    """Test that updating a command logs to audit."""
    self.storage.add_command("panic", "breathe", "U123")
    self.storage.add_command("panic", "take a breath", "U456")

    audit = self.storage.get_audit_log(limit=10)
    self.assertEqual(len(audit), 2)

    # Most recent first
    self.assertEqual(audit[0]['action'], "update")
    self.assertEqual(audit[0]['user_id'], "U456")
    self.assertEqual(audit[1]['action'], "create")
    self.assertEqual(audit[1]['user_id'], "U123")

  def test_audit_log_delete(self):
    """Test that deleting a command logs to audit."""
    self.storage.add_command("panic", "breathe", "U123")
    self.storage.delete_command("panic", "U456")

    audit = self.storage.get_audit_log(limit=10)
    self.assertEqual(len(audit), 2)

    # Most recent first
    self.assertEqual(audit[0]['action'], "delete")
    self.assertEqual(audit[0]['trigger'], "panic")
    self.assertEqual(audit[0]['response'], "breathe")
    self.assertEqual(audit[0]['user_id'], "U456")

  def test_audit_log_limit(self):
    """Test that audit log respects limit parameter."""
    # Create 5 commands
    for i in range(5):
      self.storage.add_command(f"cmd{i}", f"response{i}", "U123")

    # Get only 3
    audit = self.storage.get_audit_log(limit=3)
    self.assertEqual(len(audit), 3)

    # Get all
    audit_all = self.storage.get_audit_log(limit=100)
    self.assertEqual(len(audit_all), 5)

if __name__ == '__main__':
  unittest.main()
