# Generated by Django 4.1 on 2024-03-20 06:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_notification_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='thinking',
            field=models.TextField(max_length=250, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='mypost',
            field=models.FileField(null=True, upload_to='myposts'),
        ),
    ]
