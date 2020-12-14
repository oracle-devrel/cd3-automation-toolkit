from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
import os

REGION_CHOICES = (
("", "select"), ("us-ashburn-1", "us-ashburn-1"), ("us-phoenix-1", "us-phoenix-1"), ("uk-london-1", "uk-london-1"),
("eu-frankfurt-1", "eu-frankfurt-1"), ("ca-toronto-1", "ca-toronto-1"), ("ap-tokyo-1", "ap-tokyo-1"),
("ap-seoul-1", "ap-seoul-1"), ("ap-mumbai-1", "ap-mumbai-1"), ("ap-sydney-1", "ap-sydney-1"),
("sa-saopaulo-1", "sa-saopaulo-1"), ("eu-zurich-1", "eu-zurich-1"))

#NETWORK_CHOICES = (('Create Network', 'Create Network'), ('Modify Network ', 'Modify Network'),
    #               ('Modify Security Rules & Route Rules', 'Modify Security Rules & Route Rules'),
     #              ('Export Security Rule& Route Rules', 'Export Security Rule & Route Rules'))


def file_upload_path(instance, filename):
    user = instance.Username.replace(' ', '_')
    return '{0}/confidential/{1}-{2}'.format(user, instance.Stack_Name, filename)


def file_upload_path_excel(instance, filename):
    user = instance.Username.replace(' ', '_')
    file_path = os.path.join(settings.MEDIA_ROOT, 'users', user, 'Excel', instance.Stack_Name + '-' + filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return 'users/{0}/Excel/{1}-{2}'.format(user, instance.Stack_Name, filename)


class Tenancy(models.Model):
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['Stack_Name', 'Username'], name='Customer already exist')
        ]

    Stack_Name = models.CharField(max_length=256, verbose_name="Customer Name")
    Username = models.CharField(max_length=256)
    Tenancy_OCID = models.CharField(max_length=256)
    Fingerprint = models.CharField(max_length=256)
    User_OCID = models.CharField(max_length=256)
    Region = models.CharField(max_length=256, choices=REGION_CHOICES)
    CD3_Excel = models.FileField(upload_to=file_upload_path_excel, verbose_name="CD3 Excel(xlsx/xls format)")
    Key_File = models.FileField(verbose_name="Key File (.pem)")
    Compartment = models.BooleanField(default=False, verbose_name="Compartments")
    Groups = models.BooleanField(default=False, verbose_name="Groups,Policies")
    Network = models.CharField(max_length=256,  default=None, blank=True, null=True) #choices=NETWORK_CHOICES,
    NSG = models.BooleanField(default=False, verbose_name="Network Security Groups")
    Instance = models.BooleanField(default=False, verbose_name="Instances")
    Block_Volume = models.BooleanField(default=False, verbose_name="Block Volumes")
    RM = models.BooleanField(default=False, verbose_name="Resource Manager(Plan Only)")
    Created_Date = models.DateTimeField(default=timezone.now)
    Stack_Update = models.BooleanField(default=False)
    Terraform_Files = models.CharField(max_length=256)
    Compartment_Name = models.CharField(max_length=256, verbose_name="Resource Manager Compartment Name", blank=True, null=True)
    Export_Compartment_Name = models.CharField(max_length=256, blank=True, null=True)
    Instance_SSH_Public_Key = models.CharField(max_length=500, blank=True, null=True)
    Instance_SSH_Public_Value = models.CharField(max_length=500, blank=True, null=True)
    Stack_OCID = models.CharField(max_length=5000, blank=True, null=True)

    def __str__(self):
        return self.Stack_Name

    def get_absolute_url(self):
        return reverse('vcn:tenancy_detail', kwargs={'pk': self.pk})
