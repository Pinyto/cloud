# Generated by Django 2.2.1 on 2019-05-24 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('keyserver', '0002_auto_20150213_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='N',
            field=models.CharField(max_length=1400),
        ),
        migrations.AlterField(
            model_name='account',
            name='d',
            field=models.CharField(max_length=1400),
        ),
        migrations.AlterField(
            model_name='account',
            name='p',
            field=models.CharField(max_length=800),
        ),
        migrations.AlterField(
            model_name='account',
            name='q',
            field=models.CharField(max_length=800),
        ),
    ]
