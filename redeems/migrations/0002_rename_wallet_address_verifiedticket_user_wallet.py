# Generated by Django 4.2.3 on 2023-10-06 14:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("redeems", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="verifiedticket",
            old_name="wallet_address",
            new_name="user_wallet",
        ),
    ]
