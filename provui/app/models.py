from __future__ import unicode_literals

from django.db import models

import os

from django.conf import settings
# Create your models here.
class Domain(models.Model):
    dom = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'dom'

class Idd_data(models.Model):
    idd = models.CharField(max_length=255, blank=False, null=False)
    name = models.CharField(max_length=255, blank=False, null=False, primary_key=True)
    storage = models.CharField(max_length=255, blank=False, null=False)
    api = models.CharField(max_length=255, blank=False, null=False)
    dccode = models.CharField(max_length=255, blank=False, null=False)
    custcode = models.CharField(max_length=255, blank=False, null=False)
    customer = models.CharField(max_length=255, blank=False, null=True)
    zone = models.CharField(max_length=255, blank=False, null=True)

    class Meta:
        managed = True
        db_table = 'idd_data'

class Shapes(models.Model):
    shape_name  = models.CharField(max_length=255, blank=False, null=False)
    ram = models.CharField(max_length=255, blank=False, null=False)
    user = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'shape'

class Tier(models.Model):
    tier_name = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'tier'

class Instance(models.Model):
    inst_name = models.CharField(max_length=255, blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'instance'

class Image(models.Model):
    image_name = models.CharField(max_length=255, blank=False, null=False)
    user = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'image'

class SSHkeys(models.Model):
    ssh_name = models.CharField(max_length=255, blank=False, null=False)
    user = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'sshkeys'

class Inventory(models.Model):
    authDomain = models.CharField(max_length=255, blank=False, null=False)
    url = models.CharField(max_length=255, blank=False, null=False)
    dccode = models.CharField(max_length=255, blank=False, null=False)
    custcode = models.CharField(max_length=255, blank=False, null=False)
    account = models.CharField(max_length=255, blank=False, null=False)
    size = models.CharField(max_length=255, blank=False, null=False)
    shape = models.CharField(max_length=255, blank=False, null=False)
    image = models.CharField(max_length=255, blank=False, null=False)
    datavolsize = models.CharField(max_length=255, blank=False, null=True)
    appinstance = models.CharField(max_length=255, blank=False, null=True)
    backupvolsize = models.CharField(max_length=255, blank=False, null=True)
    hostlabel = models.CharField(max_length=255, blank=False, null=True)
    seclist = models.CharField(max_length=255, blank=False, null=True)
    tier = models.CharField(max_length=255, blank=False, null=True)
    instance = models.CharField(max_length=255, blank=False, null=True)
    ssh = models.CharField(max_length=255, blank=False, null=True)
    pagevolsize = models.CharField(max_length=255, blank=False, null=True)
    emvolsize = models.CharField(max_length=255, blank=False, null=True)
    datacenter = models.CharField(max_length=255, blank=False, null=True)
    user = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'inventory'

def generate_filename(instance, filename):
    return os.path.join('documents', str(instance.user), filename)

class Document(models.Model):
    docfile = models.FileField(upload_to=generate_filename)
    user = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return '%s' % (self.docfile.name)

    def delete(self, *args, **kwargs):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.docfile.name))
        super(Document, self).delete(*args, **kwargs)



