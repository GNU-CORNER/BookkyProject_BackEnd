# Generated by Django 4.0.3 on 2022-04-05 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bookky', '0004_book_thumbnailimage_user_loginmethod'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='pushToken',
            field=models.TextField(blank=True, null=True),
        ),
    ]
