# Generated by Django 3.0.1 on 2020-01-20 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20200120_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userrequest',
            name='nodes',
            field=models.CharField(choices=[('MSC', 'Moscow'), ('TST1', 'Test1')], max_length=300),
        ),
    ]
