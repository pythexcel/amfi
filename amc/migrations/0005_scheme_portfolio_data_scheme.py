# Generated by Django 2.2.2 on 2019-07-10 13:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('todo', '0016_auto_20190701_1247'),
        ('amc', '0004_auto_20190710_1327'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheme_portfolio_data',
            name='scheme',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='todo.Scheme'),
            preserve_default=False,
        ),
    ]