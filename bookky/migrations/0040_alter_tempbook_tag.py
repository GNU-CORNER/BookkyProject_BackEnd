# Generated by Django 4.0.3 on 2022-06-02 00:48

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookky', '0039_alter_anycomment_like_alter_marketcomment_like_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tempbook',
            name='TAG',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True), default=[], size=50),
        ),
    ]