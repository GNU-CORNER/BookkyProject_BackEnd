# Generated by Django 4.0.3 on 2022-04-17 22:37

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookky', '0010_book_thumbnailimage_alter_anycomment_createat_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anycommunity',
            name='like',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True), null=True, size=10000000),
        ),
    ]
