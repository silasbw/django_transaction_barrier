# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TransactionCommitBarrier'
        db.create_table('django_transaction_barrier_transactioncommitbarrier', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=32, db_index=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, db_index=True, blank=True)),
        ))
        db.send_create_signal('django_transaction_barrier', ['TransactionCommitBarrier'])


    def backwards(self, orm):
        # Deleting model 'TransactionCommitBarrier'
        db.delete_table('django_transaction_barrier_transactioncommitbarrier')


    models = {
        'django_transaction_barrier.transactioncommitbarrier': {
            'Meta': {'object_name': 'TransactionCommitBarrier'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '32', 'db_index': 'True'})
        }
    }

    complete_apps = ['django_transaction_barrier']
