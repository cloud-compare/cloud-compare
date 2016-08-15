from django.conf.urls import url

from . import view_aws
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # AWS Views
    url(r'^aws/?$', views.aws, name='aws'),
    url(r'^aws/offer_code=(.+)/product_family=(.+)/compute_instance=(.+)/?$',
        view_aws.aws_compute_instance, name='aws_compute_instance'),
    url(r'^aws/offer_code=(.+)/product_family=(.+)/?$',
        view_aws.aws_offer_family, name='aws_offer_family'),

    url(r'^gcp/?$', views.gcp, name='gcp'),
    url(r'^gcp/ptype=(.+)/psubtype=(.+)/?$', views.gcp_ptype_psubtype,
        name='gcp_ptype_psubtype'),
]
