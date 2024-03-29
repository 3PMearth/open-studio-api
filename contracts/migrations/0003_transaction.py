# Generated by Django 4.2.3 on 2023-07-28 14:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("contracts", "0002_contract_active"),
    ]

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("tx_hash", models.CharField(max_length=128, verbose_name="트랜잭션 해시")),
                (
                    "from_address",
                    models.CharField(max_length=128, verbose_name="보내는 주소"),
                ),
                (
                    "to_address",
                    models.CharField(
                        blank=True, max_length=128, null=True, verbose_name="받는 주소"
                    ),
                ),
                (
                    "amount",
                    models.IntegerField(blank=True, null=True, verbose_name="수량"),
                ),
                (
                    "gas_used",
                    models.IntegerField(blank=True, null=True, verbose_name="사용된 가스"),
                ),
                (
                    "gas_price",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="가스 가격(gwei)"
                    ),
                ),
                (
                    "status",
                    models.IntegerField(blank=True, null=True, verbose_name="상태"),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "contract",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="transactions",
                        to="contracts.contract",
                        verbose_name="컨트랙트",
                    ),
                ),
            ],
            options={"verbose_name": "트랜잭션", "verbose_name_plural": "트랜잭션",},
        ),
    ]
