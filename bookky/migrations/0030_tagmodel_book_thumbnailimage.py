# Generated by Django 4.0.3 on 2022-05-24 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookky', '0029_book_thumbnailimage_hotcommunity_createat_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagModel',
            fields=[
                ('TMID', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('searchName', models.CharField(max_length=255)),
            ],
        ),

    ]
