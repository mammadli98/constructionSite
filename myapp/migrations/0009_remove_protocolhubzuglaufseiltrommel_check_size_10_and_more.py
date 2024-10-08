# Generated by Django 4.2.1 on 2024-09-23 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_remove_protocolhubzugmassseiltrommel_check_size_10_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='protocolhubzuglaufseiltrommel',
            name='check_size_10',
        ),
        migrations.RemoveField(
            model_name='protocolhubzuglaufseiltrommel',
            name='check_size_4a',
        ),
        migrations.RemoveField(
            model_name='protocolhubzuglaufseiltrommel',
            name='device',
        ),
        migrations.RemoveField(
            model_name='protocolhubzuglaufseiltrommel',
            name='hoist',
        ),
        migrations.RemoveField(
            model_name='protocolhubzuglaufseiltrommel',
            name='measure',
        ),
        migrations.RemoveField(
            model_name='protocolhubzuglaufseiltrommel',
            name='position_tolerance_11',
        ),
        migrations.AddField(
            model_name='protocolhubzuglaufseiltrommel',
            name='component',
            field=models.TextField(blank=True, null=True, verbose_name='Benennung/Component'),
        ),
        migrations.AlterField(
            model_name='protocolhubzuglaufseiltrommel',
            name='baustelle',
            field=models.TextField(blank=True, null=True, verbose_name='Baustelle'),
        ),
    ]
