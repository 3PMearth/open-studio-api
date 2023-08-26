# Generated by Django 4.2.3 on 2023-08-26 17:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0006_user_created_at_user_updated_at"),
        ("tokens", "0009_alter_token_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="Order",
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
                ("order_number", models.CharField(max_length=128, verbose_name="주문번호")),
                (
                    "currency",
                    models.CharField(
                        choices=[("KRW", "KRW"), ("USD", "USD")],
                        max_length=16,
                        verbose_name="통화",
                    ),
                ),
                ("sum_price", models.CharField(max_length=32, verbose_name="총 가격")),
                ("sum_amount", models.IntegerField(verbose_name="총 수량")),
                ("country_code", models.CharField(max_length=16, verbose_name="국가코드")),
                ("phone_number", models.CharField(max_length=64, verbose_name="전화번호")),
                (
                    "order_status",
                    models.CharField(
                        choices=[
                            ("CREATED", "CREATED"),
                            ("SUCCESS", "SUCCESS"),
                            ("ERROR", "ERROR"),
                            ("CANCEL", "CANCEL"),
                        ],
                        max_length=32,
                        verbose_name="주문상태",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "buyer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="orders",
                        to="users.user",
                        verbose_name="구매자",
                    ),
                ),
            ],
            options={"verbose_name": "주문", "verbose_name_plural": "주문",},
        ),
        migrations.CreateModel(
            name="OrderToken",
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
                ("amount", models.IntegerField(verbose_name="수량")),
                ("price", models.CharField(max_length=32, verbose_name="가격")),
                (
                    "currency",
                    models.CharField(
                        choices=[("KRW", "KRW"), ("USD", "USD")],
                        max_length=16,
                        verbose_name="통화",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="order_tokens",
                        to="orders.order",
                        verbose_name="주문",
                    ),
                ),
                (
                    "token",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="order_tokens",
                        to="tokens.token",
                        verbose_name="토큰",
                    ),
                ),
            ],
            options={"verbose_name": "주문 토큰 상세", "verbose_name_plural": "주문 토큰 상세",},
        ),
    ]