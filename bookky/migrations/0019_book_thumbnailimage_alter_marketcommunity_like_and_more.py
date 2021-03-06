# Generated by Django 4.0.3 on 2022-05-11 23:51

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('bookky', '0018_book_thumbnailimage_alter_review_like'),
    ]

    operations = [

        migrations.AlterField(
            model_name='marketcommunity',
            name='like',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True), default=[], null=True, size=10000000),
        ),
        migrations.AlterField(
            model_name='qnacommunity',
            name='like',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True), default=[], null=True, size=10000000),
        ),
        migrations.CreateModel(
            name='RecommendBook',
            fields=[
                ('RBID', models.BigAutoField(primary_key=True, serialize=False)),
                ('BID', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), null=True, size=30)),
                ('TID', models.ForeignKey(default=150, on_delete=django.db.models.deletion.CASCADE, to='bookky.tag')),
                ('UID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookky.user')),
            ],
        ),
    ]
