from django.db import models

# Create your models here.

from datetime import datetime
# Create your models here.


class MFDownload(models.Model):
    amc_id = models.IntegerField(null=False)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(null=True)
    retry = models.IntegerField(null=False, default=0)
    has_data = models.BooleanField(null=False, default=True)


class AMC(models.Model):
    name = models.CharField(max_length=255, unique=True)


class Scheme(models.Model):
    amc = models.ForeignKey(
        'AMC',
        on_delete=models.CASCADE,
    )
    scheme_category = models.CharField(max_length=255, null=False)
    scheme_type = models.CharField(max_length=255, null=False)
    scheme_sub_type = models.CharField(max_length=255, null=False)
    fund_code = models.CharField(max_length=255, null=False, unique=True)
    fund_name = models.CharField(max_length=255, null=False)
    fund_option = models.CharField(max_length=255, null=False)
    fund_type = models.CharField(max_length=255, null=False)

    class Meta:
        unique_together = ("amc", "fund_code")


class Nav(models.Model):
    scheme = models.ForeignKey(
        'Scheme',
        on_delete=models.CASCADE,
    )
    nav = models.FloatField(null=False)
    date = models.DateField(null=False)

    class Meta:
        unique_together = ("scheme", "date")
