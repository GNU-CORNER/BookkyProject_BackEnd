# Generated by Django 4.0.3 on 2022-05-24 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookky', '0031_tempbook_book_thumbnailimage'),
    ]

    operations = [
        migrations.AddField(
            model_name='tempbook',
            name='searchName',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
