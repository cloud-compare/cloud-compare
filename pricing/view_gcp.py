"""Views on the GCP (Google) Table."""

from models import GCP


# Price per month 
# TBD ### Work in GCP discount curve
def gcp_per_year(price_per_hour):
    return price_per_hour * 8760 * 0.7


def get_gcp_vmimage(image):

    gcp = GCP.objects.filter(pargs=image)
    memory = gcp[0].memory
    cores = gcp[0].cores
    core_type = 'Dedicated'
    if (cores == 0):
        core = 1
        core_type = 'Shared'

    specs = {
              'memory': memory,
              'cores': cores,
              'core_type': core_type
            }

    # Get per hour prices
    base = gcp.get(preemptible=False)
    base_p = {
               'us': {
                       'per_hour': base.us,
                       'per_year': gcp_per_year(base.us)
                     },
               'asia': {
                        'per_hour': base.asia,
                        'per_year': gcp_per_year(base.asia)
                       },
               'europe': {
                         'per_hour': base.europe,
                         'per_year': gcp_per_year(base.europe)
                      },
             }

    # Per anything larger than an hour makes no sense for preemptible
    preempt = gcp.get(preemptible=True)
    preempt_p = {
               'us': {
                       'per_hour': preempt.us,
                     },
               'asia': {
                        'per_hour': preempt.asia,
                       },
               'europe': {
                         'per_hour': preempt.europe,
                      },
             }

    prices = {
               'base': base_p,
               'preempt': preempt_p,
             }

    args = {
             'offer_code': 'VMIMAGE',
             'product_family': image,
             'specs': specs,
             'prices': prices,
           }
    return args
