# Generated by Django 4.0.3 on 2022-05-12 20:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookky', '0019_book_thumbnailimage_alter_marketcommunity_like_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageStorage',
            fields=[
                ('ImageID', models.BigAutoField(primary_key=True, serialize=False)),
                ('imageTitle', models.TextField()),
                ('imageFile', models.ImageField(blank=True, null=True, upload_to='')),
                ('content', models.TextField()),
            ],
        )

    ]