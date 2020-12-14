from django import forms
from .models import Tenancy

NETWORK_CHOICES = (('create_ntk', 'Create Network'), ('modify_ntk', 'Modify Network'),
                   ('modify_secrt', 'Modify Security Rules & Route Rules'),
                   ('export_secrt', 'Export Security Rules & Route Rules'))

class TenancyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(TenancyForm, self).__init__(*args, **kwargs)
        # self.fields['Region'].widget.attrs['empty_label'] = 'select'

    Network = forms.ChoiceField(choices=NETWORK_CHOICES, widget=forms.RadioSelect(), required=False)
    class Meta:
        unique_together = ('Stack_Name', 'Username')
        model = Tenancy
        fields = ['Stack_Name', 'Tenancy_OCID', 'Fingerprint', 'User_OCID', 'Region', 'Compartment',
                  'Groups', 'Network', 'Export_Compartment_Name', 'NSG', 'Instance', 'Block_Volume', 'RM', 'Compartment_Name',
                  'Key_File', 'CD3_Excel', 'Instance_SSH_Public_Key','Instance_SSH_Public_Value']
        widgets = {
            'Network': forms.RadioSelect(attrs={'required': False}),
            'Export_Compartment_Name': forms.TextInput(attrs={'placeholder' : 'Security/Route rules compartment'}),
            'Instance_SSH_Public_Key': forms.TextInput(attrs={'placeholder' : 'SSH Key Name'}),
            'Instance_SSH_Public_Value': forms.TextInput(attrs={'placeholder' : 'SSH Key Value'}),
            'Instance': forms.CheckboxInput(attrs={'disabled':True}),
            'Block_Volume': forms.CheckboxInput(attrs={'disabled':True}),
          }


    # def full_clean(self):
    #     super(TenancyForm, self).full_clean()
    #     try:
    #         self.instance.validate_unique()
    #     except forms.ValidationError as e:
    #         self._update_errors(e)

    # def clean(self):
    #     cleaned_data = self.cleaned_data
    #     user = cleaned_data.get('Username')
    #     stk = cleaned_data.get('Stack_Name')
    #     query = Tenancy.objects.filter(Username=user)
    #
    #     for q in query:
    #         if q in stk:
    #             raise forms.ValidationError("The customer already exist")
    #     return cleaned_data




class UpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('label_suffix', '')
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.initial['Groups'] = False
        self.initial['Network'] = False
        self.initial['NSG'] = False
        self.initial['Instance'] = False
        self.initial['Block_Volume'] = False
        self.initial['RM'] = False

    Network = forms.ChoiceField(choices=NETWORK_CHOICES, widget=forms.RadioSelect(), required=False)
    class Meta:
        unique_together = ('Stack_Name', 'Username')
        model = Tenancy
        fields = ['Stack_Name', 'Tenancy_OCID', 'Fingerprint', 'User_OCID', 'Region', 'Compartment',
                  'Groups', 'Network', 'Export_Compartment_Name', 'NSG', 'Instance', 'Block_Volume', 'RM', 'Compartment_Name',
                  'Key_File', 'CD3_Excel','Instance_SSH_Public_Key','Instance_SSH_Public_Value']

        widgets = {
            'Network': forms.RadioSelect(),
            'Export_Compartment_Name': forms.TextInput(attrs={'placeholder': 'Security/Route rules compartment'}),
            'Instance_SSH_Public_Key': forms.TextInput(attrs={'placeholder': 'SSH Key Name'}),
            'Instance_SSH_Public_Value': forms.TextInput(attrs={'placeholder': 'SSH Key Value'}),
            'Instance': forms.CheckboxInput(attrs={'disabled': True}),
            'Block_Volume': forms.CheckboxInput(attrs={'disabled': True}),
            'Stack_Name': forms.TextInput(attrs={'readonly': True}),
        }


class PrivatekeyForm(forms.ModelForm):
    class Meta:
        model = Tenancy
        fields = ['Key_File']
