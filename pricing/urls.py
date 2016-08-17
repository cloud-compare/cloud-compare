from django.conf.urls import url

from . import view_aws
from . import view_gcp

urlpatterns = [
    # AWS Views
    url(r'^aws/offer_code=(.+)/product_family=(.+)/compute_instance=(.+)/?$',
        view_aws.aws_compute_instance, name='aws_compute_instance'),
    url(r'^aws/offer_code=(.+)/product_family=(.+)/?$',
        view_aws.aws_offer_family, name='aws_offer_family'),

    # GCP View
    url(r'^gcp/ptype=(.+)/psubtype=(.+)/?$', view_gcp.gcp_ptype_psubtype,
        name='gcp_ptype_psubtype'),
    url(r'^gcp/vmimage=(.+)/?$', view_gcp.gcp_vmimage, name='gcp_vmimage'),
]
