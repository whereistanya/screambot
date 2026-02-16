#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import threading
import logging
from contextlib import contextmanager
from typing import List, Dict, Optional
from datetime import datetime

class StorageManager:
  """Thread-safe SQLite storage for screambot custom commands."""

  def __init__(self, db_path: str = "screambot.db"):
    self.db_path = db_path
    self._local = threading.local()
    self._init_db()

  def _get_connection(self) -> sqlite3.Connection:
    """Get thread-local database connection."""
    if not hasattr(self._local, 'conn'):
      conn = sqlite3.connect(self.db_path, check_same_thread=False, isolation_level=None)
      conn.row_factory = sqlite3.Row
      # Enable WAL mode for better concurrency
      conn.execute('PRAGMA journal_mode=WAL')
      self._local.conn = conn
    return self._local.conn

  @contextmanager
  def _transaction(self):
    """Context manager for database transactions."""
    conn = self._get_connection()
    try:
      yield conn
      conn.commit()
    except Exception as e:
      conn.rollback()
      logging.error(f"Database transaction failed: {e}")
      raise

  def _init_db(self):
    """Initialize database schema."""
    with self._transaction() as conn:
      # Custom commands table
      conn.execute("""
        CREATE TABLE IF NOT EXISTS custom_commands (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          trigger TEXT NOT NULL UNIQUE,
          response TEXT NOT NULL,
          created_by TEXT NOT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      """)

      conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_trigger
        ON custom_commands(trigger)
      """)

      # Audit log table
      conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_log (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          action TEXT NOT NULL,
          trigger TEXT NOT NULL,
          response TEXT,
          user_id TEXT NOT NULL,
          timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      """)

      conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_timestamp
        ON audit_log(timestamp DESC)
      """)

      conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_audit_trigger
        ON audit_log(trigger)
      """)

    logging.info(f"Database initialized at {self.db_path}")

  def log_audit(self, action: str, trigger: str, user_id: str, response: str = None):
    """Log an action to the audit log.

    Args:
      action: "create", "update", or "delete"
      trigger: The command trigger
      user_id: Slack user ID who performed the action
      response: The response (for create/update actions)
    """
    try:
      with self._transaction() as conn:
        conn.execute("""
          INSERT INTO audit_log (action, trigger, response, user_id)
          VALUES (?, ?, ?, ?)
        """, (action, trigger, response, user_id))
    except Exception as e:
      logging.error(f"Failed to log audit entry: {e}")

  def add_command(self, trigger: str, response: str, created_by: str) -> bool:
    """Add or update a custom command.

    Args:
      trigger: The text that triggers the command (lowercased)
      response: What the bot responds with
      created_by: Slack user ID of creator

    Returns:
      True if successful, False otherwise
    """
    try:
      # Validate inputs for defense in depth
      if not trigger or len(trigger) < 2 or len(trigger) > 100:
        logging.error(f"Invalid trigger length: {len(trigger) if trigger else 0}")
        return False
      if not response or len(response) > 500:
        logging.error(f"Invalid response length: {len(response) if response else 0}")
        return False

      # Check if command already exists
      existing = self.get_command_creator(trigger)
      action = "update" if existing else "create"

      with self._transaction() as conn:
        conn.execute("""
          INSERT INTO custom_commands (trigger, response, created_by)
          VALUES (?, ?, ?)
          ON CONFLICT(trigger) DO UPDATE
          SET response = ?, updated_at = CURRENT_TIMESTAMP
        """, (trigger.lower(), response, created_by, response))

      # Log to audit
      self.log_audit(action, trigger.lower(), created_by, response)
      return True
    except Exception as e:
      logging.error(f"Failed to add custom command: {e}")
      return False

  def get_command(self, trigger: str) -> Optional[str]:
    """Get the response for a trigger.

    Args:
      trigger: The trigger text (case-insensitive)

    Returns:
      Response string if found, None otherwise
    """
    conn = self._get_connection()
    cursor = conn.execute("""
      SELECT response FROM custom_commands
      WHERE trigger = ?
    """, (trigger.lower(),))

    row = cursor.fetchone()
    return row['response'] if row else None

  def list_all_commands(self) -> List[Dict]:
    """List all custom commands.

    Returns:
      List of dicts with keys: trigger, response, created_by, created_at
    """
    conn = self._get_connection()
    cursor = conn.execute("""
      SELECT trigger, response, created_by, created_at
      FROM custom_commands
      ORDER BY trigger
    """)

    return [dict(row) for row in cursor.fetchall()]

  def delete_command(self, trigger: str, deleted_by: str) -> bool:
    """Delete a custom command.

    Args:
      trigger: The trigger text (case-insensitive)
      deleted_by: Slack user ID who deleted the command

    Returns:
      True if command was deleted, False if not found
    """
    try:
      # Get the command before deleting for audit log
      conn = self._get_connection()
      cursor = conn.execute("""
        SELECT response FROM custom_commands
        WHERE trigger = ?
      """, (trigger.lower(),))
      row = cursor.fetchone()

      if not row:
        return False

      response = row['response']

      with self._transaction() as conn:
        cursor = conn.execute("""
          DELETE FROM custom_commands
          WHERE trigger = ?
        """, (trigger.lower(),))

        if cursor.rowcount > 0:
          # Log deletion to audit
          self.log_audit("delete", trigger.lower(), deleted_by, response)
          return True

      return False
    except Exception as e:
      logging.error(f"Failed to delete custom command: {e}")
      return False

  def get_command_creator(self, trigger: str) -> Optional[str]:
    """Get the creator user ID for a command.

    Args:
      trigger: The trigger text (case-insensitive)

    Returns:
      User ID if found, None otherwise
    """
    conn = self._get_connection()
    cursor = conn.execute("""
      SELECT created_by FROM custom_commands
      WHERE trigger = ?
    """, (trigger.lower(),))

    row = cursor.fetchone()
    return row['created_by'] if row else None

  def get_audit_log(self, limit: int = 100) -> List[Dict]:
    """Get recent audit log entries.

    Args:
      limit: Maximum number of entries to return

    Returns:
      List of dicts with audit log entries
    """
    conn = self._get_connection()
    cursor = conn.execute("""
      SELECT action, trigger, response, user_id, timestamp
      FROM audit_log
      ORDER BY timestamp DESC, id DESC
      LIMIT ?
    """, (limit,))

    return [dict(row) for row in cursor.fetchall()]

  def close(self):
    """Close database connections."""
    if hasattr(self._local, 'conn'):
      self._local.conn.close()

# Global singleton
_storage = None

def get_storage() -> StorageManager:
  """Get or create the global storage manager."""
  global _storage
  if _storage is None:
    _storage = StorageManager()
  return _storage
