# Generated by Django 5.1.5 on 2025-01-31 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_remove_channeldata_channel_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='channeldata',
            name='source_category',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
