from django.conf.urls import url

from . import view_aws
from . import view_gcp
from . import view_main

urlpatterns = [
    # New views
    url(r'^type=(.+)/provider=(.+)/tclass=(.+)/?$',
        view_main.class_list, name='class_list'),
    url(r'^gcp/vmimage=(.+)/?$', view_gcp.gcp_vmimage, name='gcp_vmimage'),
    url(r'^aws/offer_code=(.+)/compute_instance=(.+)/?$',
        view_aws.aws_compute_instance, name='aws_compute_instance'),

]
