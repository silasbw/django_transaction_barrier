import logging

log = logging.getLogger(__name__)


def get_transaction_metadata(cursor):
  """Return PostgreSQL-specific transaction ID."""
  cursor.execute('SELECT txid_current();')
  txid = cursor.fetchone()[0]
  return txid


def is_transaction_complete(cursor, txid):
  """Test if transaction ID is finished (committed or aborted."""
  # See http://www.postgresql.org/docs/9.1/static/functions-info.html for
  # descriptions of the postgres system functions.
  cursor.execute('SELECT txid_current_snapshot();')
  # "txid_snapshot's textual representation is xmin:xmax:xip_list.
  # For example 10:20:10,14,15 means xmin=10, xmax=20, xip_list=10, 14, 15."
  xmin, xmax, xip_list = cursor.fetchone()[0].split(':')
  xmin = long(xmin)
  xmax = long(xmax)
  xip_list = map(long, xip_list.split(',')) if xip_list else []

  # If the transaction is finished according to the postgres system functions,
  # but we can't find the TransactionCommitBarrier, we know the transaction is
  # aborted.

  # xmin is the "earliest transaction ID (txid) that is still active. All
  # earlier transactions will either be committed and visible, or rolled
  # back and dead."
  if txid < xmin:
    log.info('Transaction(%lu) finished xmin', txid)
    return True

  # "A txid that is xmin <= txid < xmax and not in this list was already
  # completed at the time of the snapshot, and thus either visible or dead
  # according to its commit status."
  if xmin <= txid and txid < xmax and txid not in xip_list:
    log.info('Transaction(%lu) finished xip_list', txid)
    return True

  return False


def get_debug_info(cursor):
  cursor.execute('SELECT txid_current_snapshot();')
  return cursor.fetchone()[0]
