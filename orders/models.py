from django.db import models

# Create your models here.
class Order(models.Model):
    """
    Order model for token sale
    """
    class CurrencyChoice(models.TextChoices):
        KRW = 'krw', 'krw'
        USD = 'usd', 'usd'

    class OrderStatusChoice(models.TextChoices):
        CREATED = 'created', 'created'
        SUCCESS = 'success', 'success'
        REFUND = 'refund', 'refund'
        ERROR = 'error', 'error'
        CANCEL = 'cancel', 'cancel'

    order_number = models.CharField(max_length=128, verbose_name="주문번호")
    buyer = models.ForeignKey("users.User", on_delete=models.CASCADE,
                               related_name='orders', verbose_name="구매자")
    currency = models.CharField(max_length=16, verbose_name="통화",
                                choices=CurrencyChoice.choices)
    sum_price = models.CharField(max_length=32, verbose_name="총 가격")
    sum_amount = models.IntegerField(verbose_name="총 수량")
    country_code = models.CharField(max_length=16, verbose_name="국가코드")
    phone_number = models.CharField(max_length=64, verbose_name="전화번호")
    order_status = models.CharField(max_length=32, verbose_name="주문상태",
                                    choices=OrderStatusChoice.choices)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order_number}"

    class Meta:
        verbose_name = "주문"
        verbose_name_plural = "주문"

class OrderToken(models.Model):
    """
    OrderToken model for token sale, each order has multiple tokens
    """
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE,
                              related_name='order_tokens', verbose_name="주문")
    token = models.ForeignKey("tokens.Token", on_delete=models.CASCADE,
                              related_name='order_tokens', verbose_name="토큰")
    amount = models.IntegerField(verbose_name="수량")
    price = models.CharField(max_length=32, verbose_name="가격")
    currency = models.CharField(max_length=16, verbose_name="통화",
                                choices=Order.CurrencyChoice.choices)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order.order_number} - {self.token.name}"

    class Meta:
        verbose_name = "주문 토큰 상세"
        verbose_name_plural = "주문 토큰 상세"
