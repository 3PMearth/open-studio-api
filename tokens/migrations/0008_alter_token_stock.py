# Generated by Django 4.2.3 on 2023-07-29 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tokens", "0007_alter_token_contract_delete_contract"),
    ]

    operations = [
        migrations.AlterField(
            model_name="token",
            name="stock",
            field=models.IntegerField(default=1, verbose_name="재고(amount)"),
        ),
    ]
