# Generated by Django 2.2.2 on 2019-09-18 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('amc', '0011_scheme_name_mismatch'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheme_name_mismatch',
            name='aum',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='scheme_name_mismatch',
            name='inception',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]
