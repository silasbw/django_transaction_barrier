#!/bin/sh

set -e

cd /django_transaction_barrier/testproject

C_FORCE_ROOT=1 celery worker -l info -A testproject.celery_settings
