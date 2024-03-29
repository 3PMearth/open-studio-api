# Generated by Django 4.2.3 on 2023-07-28 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contracts", "0003_transaction"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="nonce",
            field=models.IntegerField(default=0, verbose_name="nonce"),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="from_address",
            field=models.CharField(max_length=128, verbose_name="보내는 주소(서명주체)"),
        ),
    ]
