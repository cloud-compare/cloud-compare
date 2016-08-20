"""Views on the AWS Table."""
from django.http import HttpResponse
from django.shortcuts import render
from django.db.models import Q
from django.db.models import Count
from django.db.models import Min, Max

from pricing.models import AWS, UIAWSSummary

# This the new
def get_aws_compute_instance(instance_type):
    instance = UIAWSSummary.objects.get(name=instance_type)

    args = {
             'instance_type': instance_type,
             'instance': instance,
           }
    return args


