
from django import forms


class EC2InstanceForm(forms.Form):

    ttpicks = [('OnDemand', 'OnDemand'), ('Reserved', 'Reserved')]
    term_type = forms.MultipleChoiceField(
                 widget=forms.CheckboxSelectMultiple,
                 choices=ttpicks, label='Term Type')

    ospicks = [('Linux', 'Linux'),
               ('RHEL', 'RHEL'),
               ('Windows', 'Windows'),
               ('SUSE', 'SUSE'),
               ('NA', 'NA')]

    operating_system = forms.MultipleChoiceField(
                 widget=forms.CheckboxSelectMultiple,
                 choices=ospicks, label='Operating System')

    tenpicks = [('Shared', 'Shared'),
                ('Dedicated', 'Dedicated'),
                ('Host', 'Host')]
    tenancy = forms.MultipleChoiceField(
                    widget=forms.CheckboxSelectMultiple,
                    choices=tenpicks, label='Tenancy')
