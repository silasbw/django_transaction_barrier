import datetime
import logging

from django.conf import settings
from django.db import connections
from django.db import DEFAULT_DB_ALIAS

from django_transaction_barrier import postgresql
from django_transaction_barrier import sqlite3
from django_transaction_barrier.models import TransactionCommitBarrier

log = logging.getLogger(__name__)


class TransactionAborted(Exception):
  pass


def _db_backend(using):
  engine = settings.DATABASES[using]['ENGINE']
  return {'django.db.backends.postgresql_psycopg2': postgresql,
          'django.db.backends.sqlite3': sqlite3}[engine]


def get_debug_info(barrier=None):
  info = []
  using = DEFAULT_DB_ALIAS
  if barrier:
    using = barrier['using']
    info.append(u'[Barrier %s]' % unicode(barrier))
    commit_barriers = TransactionCommitBarrier.objects.using(using).filter(
        uuid=barrier['uuid'])
    if commit_barriers:
      info.append(u'[TransactionCommitBarrier: %s]' % (
          unicode(commit_barriers[0])))
  cursor = connections[using].cursor()
  info.append(u'[Backend: %s]' % _db_backend(using).get_debug_info(cursor))
  return u','.join(info)


def new_transaction_barrier(using=None):
  """Create a new transaction barrier and return it.

  The barrier implicity supports only 1 waiter. In other words, for a given
  barrier, only one process/thread/task should call poll_transaction_barrier.
  If more than one calls poll_transaction_barrier the semantics are undefined.
  The caller should consider the barrier opaque and specific to DB backend
  type. ``using`` is the Django DB alias to use."""
  using = using or DEFAULT_DB_ALIAS

  # First save a commit barrier.
  commit_barrier = TransactionCommitBarrier()
  commit_barrier.save(using=using)

  # Second get the current transaction metadata (e.g., a Postgres transaction
  # ID). Using the metadata the backend determines if the transaction finishes
  # (either aborts of commits).
  cursor = connections[using].cursor()
  metadata = _db_backend(using).get_transaction_metadata(cursor)

  return dict(uuid=commit_barrier.uuid, metadata=metadata, using=using)


def delete_transaction_barrier(barrier):
  (TransactionCommitBarrier.objects.using(barrier['using'])
   .get(uuid=barrier['uuid']).delete())


def poll_transaction_barrier(barrier):
  """Poll the transaction barrier.

  Return True if the barrier is satisfied, return False if it's still waiting.
  Raise TransactionAborted if the transaction was aborted.
  """
  # Optimistically poll the DB for the TransactionCommitBarrier. If it exists,
  # we know that the transaction is committed successfully.
  if _poll_transaction_commit_barrier(barrier['uuid'], barrier['using']):
    return True

  # If the transaction is finished according to the DB-specific functions,
  # but we can't find the TransactionCommitBarrier, we know the transaction is
  # aborted.
  cursor = connections[barrier['using']].cursor()
  if _db_backend(barrier['using']).is_transaction_complete(
      cursor, barrier['metadata']):
    if _poll_transaction_commit_barrier(barrier['uuid'], barrier['using']):
      return True
    raise TransactionAborted()

  return False


def reap_commit_barriers(age_in_seconds, using=None):
  """Delete all TransactionCommitBarriers older than ``age_in_seconds``.

  If an applications allocates a barrier with new_transaction_barrier, but
  fails to delete it, metadata might linger in the database.
  reap_commit_barriers is a hack to help remove that metadata. ``using`` is
  the Django DB alias to use. ``using_barrier`` is a barrier to extract the
  Django DB alias from (instead of using ``using``).

  If your application uses TransactionBarrierTask and never calls
  new_transaction_barrier directly, you can ignore this function.
  """
  using = using or DEFAULT_DB_ALIAS

  time_threshold = (
      datetime.datetime.now() - datetime.timedelta(seconds=age_in_seconds))
  TransactionCommitBarrier.objects.using(using).filter(
      creation_date__lt=time_threshold).delete()


def _poll_transaction_commit_barrier(uuid, using):
  try:
    TransactionCommitBarrier.objects.using(using).get(uuid=uuid)
    return True
  except TransactionCommitBarrier.DoesNotExist:
    return False
