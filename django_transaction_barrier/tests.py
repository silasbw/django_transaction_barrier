#!/usr/bin/python
# coding: utf-8

# These tests require a running celery worker and CELERY_ALWAYS_EAGER=False.

from celery import task
import os
import random
import unittest
from unittest import TestCase
import time

from django.db import transaction

from django_transaction_barrier.celery import TransactionBarrierTask


def touch(file_path):
  open(file_path, 'a').close()


def random_file_path():
  return os.path.join(
      '/tmp', 'transactionbarrier_test_%s' % str(random.random()))


@task(base=TransactionBarrierTask,
      name='transaction_barrier.tests.test_decorator_task',
      require_barrier=False)
def test_decorator_task(file_path):
  touch(file_path)


class TransactionBarrierTestTask(TransactionBarrierTask):

  name = 'transaction_barrier.tests.TransactionBarrierTestTask'

  def run(self, file_path):
    touch(file_path)


class TestTransactionBarrier(TestCase):

  def test_task_apply_async_with_barrier(self):
    with transaction.atomic():
      result = TransactionBarrierTestTask.apply_async_with_barrier(
          args=(self.file_path,))
      time.sleep(5)
      self.assertFalse(os.path.isfile(self.file_path))
    result.get()
    self.assertTrue(os.path.isfile(self.file_path))

  def test_task_apply_async_with_barrier_required(self):
    with self.assertRaises(RuntimeError):
      result = TransactionBarrierTestTask.apply_async(args=(self.file_path,))
      result.get()
    self.assertFalse(os.path.isfile(self.file_path))

  def test_task_apply_with_barrier_required(self):
    with self.assertRaises(RuntimeError):
      TransactionBarrierTestTask.apply(self.file_path)

  def test_decorator_apply_async_with_barrier(self):
    with transaction.atomic():
      result = test_decorator_task.apply_async_with_barrier(
          args=(self.file_path,))
      time.sleep(5)
      self.assertFalse(os.path.isfile(self.file_path))
    result.get()
    self.assertTrue(os.path.isfile(self.file_path))

  def test_decorator_allow_apply_async(self):
    with transaction.atomic():
      result = test_decorator_task.apply_async(args=(self.file_path,))
      time.sleep(5)
      self.assertTrue(os.path.isfile(self.file_path))
    result.get()

  def test_decorator_call(self):
    with transaction.atomic():
      test_decorator_task(self.file_path)
      self.assertTrue(os.path.isfile(self.file_path))

  def test_decorator_call_allow_appy_async(self):
    test_decorator_task(self.file_path)
    self.assertTrue(os.path.isfile(self.file_path))

  def setUp(self):
    self.file_path = random_file_path()

  def tearDown(self):
    try:
      os.remove(self.file_path)
    except OSError:
      pass


if __name__ == '__main__':
  unittest.main()
