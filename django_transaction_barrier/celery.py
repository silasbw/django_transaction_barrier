from __future__ import absolute_import
import random

from celery.task import Task
from celery.exceptions import MaxRetriesExceededError

from django_transaction_barrier import delete_transaction_barrier
from django_transaction_barrier import get_debug_info
from django_transaction_barrier import new_transaction_barrier
from django_transaction_barrier import poll_transaction_barrier
from django_transaction_barrier import reap_commit_barriers
from django_transaction_barrier import TransactionAborted


class TransactionBarrierMaxRetriesError(MaxRetriesExceededError):
  def __init__(self, name, args, kwargs, barrier):
    super(TransactionBarrierMaxRetriesError, self).__init__(
        u"Can't retry %s args:%s kwargs:%s debug:%s" % (
            name, unicode(args), unicode(kwargs), get_debug_info(barrier)))

  def __call__(self):
    return self


class TransactionBarrierTask(Task):

  abstract = True  # Tell Celery not to register the Task.
  acks_late = True  # Guarantee at least once semantics.

  retry_countdown_seconds = 10
  time_limit_seconds = 4 * 60
  max_retries = time_limit_seconds / retry_countdown_seconds
  _ignore_transaction_aborted_exception = True
  require_barrier = True

  def __init__(self, *args, **kwargs):
    super(TransactionBarrierTask, self).__init__(*args, **kwargs)
    self.__post_barrier_run = self.run
    self.run = self.__pre_barrier_run

  def __pre_barrier_run(self, *args, **kwargs):
    """If invoked via apply_async_with_barrier wait on the barrier.

    Otherwise raise a RuntimeError.
    """
    if '__transaction_barrier' not in kwargs:
      if not self.require_barrier:
        return self.__post_barrier_run(*args, **kwargs)
      raise RuntimeError(
          'Did not invoke TransactionBarrierTask.apply_async_with_barrier.')
    barrier = kwargs.pop('__transaction_barrier')

    # Cleanup old commit barriers. We don't expect there to be very many
    # so we call reap_commit_barriers infrequently.
    if random.randint(1, 10000) == 1:
      reap_commit_barriers(60 * 60 * 24, using=barrier['using'])

    while True:
      try:
        if poll_transaction_barrier(barrier):
          try:
            return self.__post_barrier_run(*args, **kwargs)
          finally:
            delete_transaction_barrier(barrier)

        self.retry(countdown=self.retry_countdown_seconds,
                   max_retries=self.max_retries,
                   exc=TransactionBarrierMaxRetriesError(
                       self.name, args, kwargs, barrier))
        assert not 'reachable'
      except TransactionAborted:
        if self._ignore_transaction_aborted_exception:
          return
        raise

  @classmethod
  def apply_async_with_barrier(
      cls, args=None, kwargs=None, using=None, **options):
    """Ensures Celery calls post_barrier_run after a barrier is satisfied."""
    kwargs = dict(kwargs) if kwargs else {}
    kwargs['__transaction_barrier'] = new_transaction_barrier(using=using)
    return super(TransactionBarrierTask, cls).apply_async(
        args=args, kwargs=kwargs, **options)
