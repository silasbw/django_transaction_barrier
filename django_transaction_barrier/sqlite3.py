# Support for sqlite3 in-memory databases.
#
# sqlite implements very coarse grained locking, especially for in-memory
# databases:
#   http://www.sqlite.org/pragma.html
#   http://www.sqlite.org/lockingv3.html
#
# When poll_transaction_barrier calls get_transaction_metadata sqlite is in
# an EXCLUSIVE transaction (or autocommit). is_transaction_complete, therefore
# needs to ensure that poll_transaction_barrier has acquired a SHARED
# (or stronger) lock.


def get_transaction_metadata(cursor):
  return None


def is_transaction_complete(cursor, txid):
  # Acquire a SHARED lock by selecting from the builtin SQLITE_MASTER table.
  cursor('SELECT * from SQLITE_MASTER limit 1;')
  cursor.fetchone()
  return True


def get_debug_info(cursor):
  return u''
