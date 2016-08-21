from __future__ import unicode_literals

from django.db import models

# Create your models here.


# Google = GCP
#
# GSP Terms not yet covered:
#   FORWARDING_RULE_CHARGE_BASE {u'fixed': True, u'us': 0.025}
#   FORWARDING_RULE_CHARGE_EXTRA {u'us': 0.01}
#   sustained_use_tiers {u'0.25': 1.0, u'1.0': 0.4, u'0.75': 0.6, u'0.50': 0.8}
#   sustained_use_base 0.25
#   NETWORK_LOAD_BALANCED_INGRESS {u'us': 0.008}
class GCP(models.Model):
    ptype = models.TextField()
    psubtype = models.TextField(null=True)
    pargs = models.TextField(null=True)
    asia = models.FloatField(null=True)
    cores = models.IntegerField(null=True)
    europe = models.FloatField(null=True)
    freequota = models.TextField(null=True)
    gceu = models.TextField(null=True)
    interactiveQueries = models.TextField(null=True)
    maxNumberOfPd = models.TextField(null=True)
    maxPdSize = models.TextField(null=True)
    memory = models.FloatField(null=True)
    rhel = models.TextField(null=True)
    schedule = models.TextField(null=True)
    ssd = models.TextField(null=True)
    storage = models.TextField(null=True)
    streamingInserts = models.TextField(null=True)
    suse = models.TextField(null=True)
    tiers = models.TextField(null=True)
    us = models.FloatField(null=True)
    win = models.TextField(null=True)
    preemptible = models.NullBooleanField()


# Amazon - AWS
# This is a flattened representation of the JSON data in an AWS
# pricing file.
# Data for AWS Pricing
class AWS(models.Model):
    sku = models.TextField()

    # From 'products' JSON
    offer_code = models.TextField()
    product_family = models.TextField()

    # this is union of all fields defined for all attribute types.
    # Pulled by hand 24 July 2016.

    # != NULL when product_family='Storage'
    availability = models.TextField(null=True)

    # != NULL when product_family='AmazonEleasticCache'
    cache_engine = models.TextField(null=True)

    # != NULL when product_family='Compute Instance' or 'Database Instance'
    clock_speed = models.TextField(null=True)

    # != NULL in product='AmazonSES'
    content_type = models.TextField(null=True)

    # != NULL in 'product_family' one of:
    #   'Compute Instance', 'Database Instance', 'Cache Instance',
    #   'Dedicated Host'
    current_generation = models.TextField(null=True)
    database_edition = models.TextField(null=True)
    database_engine = models.TextField(null=True)
    dedicated_ebs_throughput = models.TextField(null=True)
    deployment_option = models.TextField(null=True)
    description = models.TextField(null=True)
    durability = models.TextField(null=True)
    ebs_optimized = models.TextField(null=True)
    ecu = models.TextField(null=True)
    endpoint_type = models.TextField(null=True)
    engine_code = models.TextField(null=True)
    enhanced_network_supported = models.TextField(null=True)
    fee_code = models.TextField(null=True)
    fee_description = models.TextField(null=True)
    from_location = models.TextField(null=True)
    from_location_type = models.TextField(null=True)
    gpu = models.TextField(null=True)
    group = models.TextField(null=True)
    group_description = models.TextField(null=True)
    instance_capacity_10xlarge = models.TextField(null=True)
    instance_capacity_2xlarge = models.TextField(null=True)
    instance_capacity_4xlarge = models.TextField(null=True)
    instance_capacity_8xlarge = models.TextField(null=True)
    instance_capacity_large = models.TextField(null=True)
    instance_capacity_medium = models.TextField(null=True)
    instance_capacity_large = models.TextField(null=True)
    instance_family = models.TextField(null=True)
    instance_type = models.TextField(null=True)
    intel_avx2_available = models.TextField(null=True)
    intel_avx_available = models.TextField(null=True)
    intel_turbo_available = models.TextField(null=True)
    io = models.TextField(null=True)
    license_model = models.TextField(null=True)
    location = models.TextField(null=True)
    location_type = models.TextField(null=True)
    max_iops_burst_performance = models.TextField(null=True)
    max_iopsvolume = models.TextField(null=True)
    max_throughputvolume = models.TextField(null=True)
    max_volume_size = models.TextField(null=True)
    memory = models.FloatField(null=True)
    network_performance = models.TextField(null=True)
    operating_system = models.TextField(null=True)
    operation = models.TextField(null=True)
    origin = models.TextField(null=True)
    physical_cores = models.TextField(null=True)
    physical_processor = models.TextField(null=True)
    pre_installed_sw = models.TextField(null=True)
    processor_architecture = models.TextField(null=True)
    processor_features = models.TextField(null=True)
    provisioned = models.TextField(null=True)
    recipient = models.TextField(null=True)
    request_description = models.TextField(null=True)
    request_type = models.TextField(null=True)
    resource_endpoint = models.TextField(null=True)
    routing_target = models.TextField(null=True)
    routing_type = models.TextField(null=True)

    # Never null. Always == offercode EXCEPT 
    # EXCEPT when == AWSDataTransfer (AWS to AWS)
    servicecode = models.TextField(null=True)     

    # != NULL when offer_code='AmazonEC2' and product_family="Dedicated Host'
    sockets = models.TextField(null=True)

    # != NULL when offer_code='AmazonS3'
    storage = models.TextField(null=True)
    storage_class = models.TextField(null=True)
    storage_media = models.TextField(null=True)
    tenancy = models.TextField(null=True)
    to_location = models.TextField(null=True)
    to_location_type = models.TextField(null=True)
    transfer_type = models.TextField(null=True)
    usage_family = models.TextField(null=True)
    usagetype = models.TextField(null=True)
    vcpu = models.IntegerField(null=True)
    volume_type = models.TextField(null=True)

    # Data from 'terms'
    term_type = models.TextField()
    offer_term_code = models.TextField()
    effective_date = models.TextField()
    # PriceDimensions
    applies_to = models.TextField(null=True)
    begin_range = models.IntegerField(null=True)
    description = models.TextField(null=True)
    end_range = models.TextField(null=True)
    price_per_unit = models.FloatField(null=True)
    rate_code = models.TextField(null=True)
    unit = models.TextField(null=True)
    # termAttributes
    lease_contract_length = models.TextField(null=True)
    purchase_option = models.TextField(null=True)


# ## UI Tables

# Prebuilt table for the main page
TYPE_CHOICES = (
    ('VirtMach', 'Virtual Machine'),
)

class UIMain(models.Model):
    # Type of entry
    type = models.TextField(choices=TYPE_CHOICES)

    # Our classification
    tclass = models.TextField()

    # Total across all providers
    total = models.IntegerField()

    # number available at google
    gcp = models.IntegerField()

    # number available at amazon
    aws = models.IntegerField()

    # number available at mocrosoft
    azure = models.IntegerField()



class UIVMSummary(models.Model):
    # Provider
    PROVIDER_CHOICES = (
        ('google', 'google'),
        ('amazon', 'amazon'),
        ('micrsoft', 'micrsoft'),
    )
    provider = models.TextField(choices=PROVIDER_CHOICES)

    # Class of instance
    tclass = models.TextField()

    # Name of instance
    name = models.TextField()

    memory = models.FloatField()

    cpu = models.IntegerField()

    # Low price in US
    price = models.FloatField()

    # url to use
    url = models.TextField()

    # current generation?
    current_generation = models.TextField(null=True)
    


# Precomputed data to populate AWS Comput instance modal
class UIAWSSummary(models.Model):
    name = models.TextField()
    memory = models.FloatField()
    vcpu = models.FloatField()
    physical_processor = models.TextField()
    clock_speed = models.TextField(null=True)
    current_generation = models.TextField(null=True)
    network_performance = models.TextField()
    storage = models.TextField()
    dedicated_ebs_throughput = models.TextField(null=True)

    # OnDemand Prices
    on_demand_shared_low = models.FloatField()
    on_demand_shared_high = models.FloatField()
    on_demand_dedicated_low = models.FloatField(null=True)
    on_demand_dedicated_high = models.FloatField(null=True)

    # Reserved 1yr prices
    reserved_1yr_noupfront_shared_low = models.FloatField(null=True)
    reserved_1yr_noupfront_shared_high = models.FloatField(null=True)
    reserved_1yr_noupfront_dedicated_low = models.FloatField(null=True)
    reserved_1yr_noupfront_dedicated_high = models.FloatField(null=True)

    reserved_1yr_upfront_shared_low = models.FloatField(null=True)
    reserved_1yr_upfront_shared_high = models.FloatField(null=True)
    reserved_1yr_upfront_dedicated_low = models.FloatField(null=True)
    reserved_1yr_upfront_dedicated_high = models.FloatField(null=True)

    reserved_1yr_upfront_dedicated_effective_low = models.FloatField(null=True)
    reserved_1yr_upfront_dedicated_effective_high = models.FloatField(null=True)

    reserved_1yr_partial_shared_low = models.FloatField(null=True)
    reserved_1yr_partial_shared_high = models.FloatField(null=True)
    reserved_1yr_partial_dedicated_low = models.FloatField(null=True)
    reserved_1yr_partial_dedicated_high = models.FloatField(null=True)

    reserved_1yr_partial_hr_shared_low = models.FloatField(null=True)
    reserved_1yr_partial_hr_shared_high = models.FloatField(null=True)
    reserved_1yr_partial_hr_dedicated_low = models.FloatField(null=True)
    reserved_1yr_partial_hr_dedicated_high = models.FloatField(null=True)

    reserved_1yr_partial_dedicated_effective_low = models.FloatField(null=True)
    reserved_1yr_partial_dedicated_effective_high = models.FloatField(null=True)

    # Reserved 3yr prices
    reserved_3yr_noupfront_shared_low = models.FloatField(null=True)
    reserved_3yr_noupfront_shared_high = models.FloatField(null=True)
    reserved_3yr_noupfront_dedicated_low = models.FloatField(null=True)
    reserved_3yr_noupfront_dedicated_high = models.FloatField(null=True)

    reserved_3yr_upfront_shared_low = models.FloatField(null=True)
    reserved_3yr_upfront_shared_high = models.FloatField(null=True)
    reserved_3yr_upfront_dedicated_low = models.FloatField(null=True)
    reserved_3yr_upfront_dedicated_high = models.FloatField(null=True)

    reserved_3yr_upfront_dedicated_effective_low = models.FloatField(null=True)
    reserved_3yr_upfront_dedicated_effective_high = models.FloatField(null=True)

    reserved_3yr_partial_shared_low = models.FloatField(null=True)
    reserved_3yr_partial_shared_high = models.FloatField(null=True)
    reserved_3yr_partial_dedicated_low = models.FloatField(null=True)
    reserved_3yr_partial_dedicated_high = models.FloatField(null=True)

    reserved_3yr_partial_hr_shared_low = models.FloatField(null=True)
    reserved_3yr_partial_hr_shared_high = models.FloatField(null=True)
    reserved_3yr_partial_hr_dedicated_low = models.FloatField(null=True)
    reserved_3yr_partial_hr_dedicated_high = models.FloatField(null=True)

    reserved_3yr_partial_dedicated_effective_low = models.FloatField(null=True)
    reserved_3yr_partial_dedicated_effective_high = models.FloatField(null=True)
