import uuid

from django.db import models


class TransactionCommitBarrier(models.Model):

  uuid = models.CharField(max_length=32, db_index=True)
  creation_date = models.DateTimeField(auto_now_add=True, db_index=True)

  def __init__(self, *args, **kwargs):
    super(TransactionCommitBarrier, self).__init__(*args, **kwargs)
    self.uuid = uuid.uuid4().hex

  def __unicode__(self):
    return u'(%s, %s)' % (self.uuid, unicode(self.creation_date))
