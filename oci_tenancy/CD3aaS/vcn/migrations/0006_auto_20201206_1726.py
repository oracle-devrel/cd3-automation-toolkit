# Generated by Django 3.1.4 on 2020-12-06 11:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vcn', '0005_auto_20201206_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tenancy',
            name='Network',
            field=models.CharField(choices=[('Create Network', 'Create Network'), ('Modify Network ', 'Modify Network'), ('Modify Security Rules & Route Rules', 'Modify Security Rules & Route Rules'), ('Export Security Rule& Route Rules', 'Export Security Rule & Route Rules')], default=None, max_length=256, null=True),
        ),
    ]
