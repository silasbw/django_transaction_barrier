# Support for sqlite3 databases.
#
# sqlite implements coarse grained locking:
#   http://www.sqlite.org/pragma.html
#   http://www.sqlite.org/lockingv3.html
#
# When poll_transaction_barrier calls get_transaction_metadata sqlite the
# connection has a RESERVED lock. is_transaction_complete, therefore
# needs to ensure that poll_transaction_barrier has acquired a RESERVED
# (or stronger) lock, which implies all previous RESERVED acquisitions are
# released.

from django.db.utils import OperationalError

import sys


def get_transaction_metadata(cursor):
  return None


def is_transaction_complete(cursor, txid):
  # Acquire a RESERVED lock by creating t table in a tx.
  cursor.execute('BEGIN TRANSACTION;')
  try:
    cursor.execute(
        'CREATE TABLE django_transaction_barrier_sqlite3_poller (c int);')
  except OperationalError as error:
    # Assume it's a 'database is locked' error
    return False
  # We have a RESERVED lock.
  cursor.execute('ROLLBACK;')
  cursor.fetchall()
  return True


def get_debug_info(cursor):
  return u''
