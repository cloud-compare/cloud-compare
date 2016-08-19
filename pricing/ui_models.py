from __future__ import unicode_literals

from django.db import models

class UIMain(models.model):
    # Type of entry
    TYPE_CHOICES = (
        ('VirtMach', 'Virtual Machine"),
    }

    type = models.TextField(choices=TYPE_CHOICES)

    # class of entry
    CLASS_CHOICES = (
        ('small', 'small'),
        ('standard', 'standard'),
        ('highcpu', 'high cpu'),
        ('highmem', 'high memory'),
        ('storage', 'storage'),
        ('gpu', 'gpu'),
    )
    class = models.TextField(choices-=CLASS_CHOICES)

    # Provider
    PROVIDER_CHOICES = (
        ('google', 'google'),
        ('amazon', 'amazon'),
        ('micrsoft', 'micrsoft'),
    }
    provier = models.TextField(choices-=PROVIDER_CHOICES)

    # availeble at google?
    gcp = models.BoolField()

    # availeble at amazon?
    aws = models.BoolField()

    # availeble at mocrosoft?
    azure = models.BoolField()
