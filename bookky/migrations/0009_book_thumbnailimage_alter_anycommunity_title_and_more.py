# Generated by Django 4.0.3 on 2022-04-15 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookky', '0008_anycommunity_title_book_thumbnailimage_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anycommunity',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='marketcommunity',
            name='title',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='qnacommunity',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]
