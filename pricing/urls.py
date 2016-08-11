from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    # AWS Views
    url(r'^aws/?$', views.aws, name='aws'),
    url(r'^aws/offer_code=(.+)/product_family=(.+)/compute_instance=(.+)/?$',
        views.aws_compute_instance, name='aws_compute_instance'),
    url(r'^aws/offer_code=(.+)/product_family=(.+)/?$',
        views.aws_prodfamily, name='aws_prodfam'),

    url(r'^gcp/?$', views.gcp, name='gcp'),
    url(r'^gcp/ptype=(.+)/psubtype=(.+)/?$', views.gcp_ptype_psubtype,
        name='gcp_ptype_psubtype'),
]
