# Generated by Django 4.2.3 on 2023-07-29 17:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0003_alter_user_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="slug",
            field=models.CharField(
                blank=True, max_length=32, null=True, verbose_name="슬러그"
            ),
        ),
    ]
