# Generated by Django 4.0.3 on 2022-06-02 00:46

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookky', '0037_alter_marketcommunity_postimage_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anycomment',
            name='like',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True), default=[], null=True, size=10000000),
        ),
        migrations.AlterField(
            model_name='marketcomment',
            name='like',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True), default=[], null=True, size=10000000),
        ),
        migrations.AlterField(
            model_name='qnacomment',
            name='like',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True), default=[], null=True, size=10000000),
        ),
    ]