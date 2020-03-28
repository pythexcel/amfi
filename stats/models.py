from django.db import models


class SchemeStats(models.Model):
    scheme = models.OneToOneField(
        'todo.Scheme',
        on_delete=models.CASCADE,
        primary_key=True,
    )
    dump = models.TextField()
    date = models.DateTimeField(auto_now_add=True, blank=True)
    calc_date = models.DateField(blank=False)
    one_year_abs_ret = models.FloatField()
    three_year_abs_ret = models.FloatField()
    three_year_cagr_ret = models.FloatField()
    five_year_abs_ret = models.FloatField()
    five_year_cagr_ret = models.FloatField()
    since_begin_abs_ret = models.FloatField()
    since_begin_cagr_ret = models.FloatField()

class SchemeRolling(models.Model):
    scheme = models.OneToOneField(
        'todo.Scheme',
        on_delete=models.CASCADE,
        primary_key=True,
    )
    rolling_data = models.TextField()
    date = models.DateTimeField(auto_now_add=True, blank=True)
    calc_date = models.DateField(blank=False)