# Generated by Django 4.2.1 on 2024-08-08 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_alter_protocolhubzugliftinghost_check_size_1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='protocolhubzugliftinghost',
            name='isExported',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='protocolhubzugliftinghost',
            name='isSaved',
            field=models.BooleanField(default=False),
        ),
    ]
