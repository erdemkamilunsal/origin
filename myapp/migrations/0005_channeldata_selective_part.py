# Generated by Django 5.1.5 on 2025-01-31 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_channeldata_source_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='channeldata',
            name='selective_part',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
