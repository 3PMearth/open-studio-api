from django.db import models


# Create your models here.
class PGDataPayment(models.Model):
    """
    PGDataPayment model for payment
    """

    class PGTypeChoice(models.TextChoices):
        KCP = 'KCP', 'KCP'
        INICIS = 'INICIS', 'INICIS'
        PAYPAL = 'PAYPAL', 'PAYPAL'
        PAYAPP = 'PAYAPP', 'PAYAPP'

    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE,
                                 related_name='pg_data_payment', verbose_name="주문")
    type = models.CharField(max_length=32, verbose_name="PG 타입",
                            choices=PGTypeChoice.choices)
    status = models.CharField(max_length=16, verbose_name="PG 상태")
    vid = models.CharField(max_length=128, verbose_name="PG 고유 거래 번호(결제요청번호)")
    method_type = models.CharField(max_length=32, verbose_name="PG 결제 수단")
    pg_message = models.CharField(max_length=128, verbose_name="PG 메시지(에러시)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vid}"

    class Meta:
        verbose_name = "PG 결제 데이터"
        verbose_name_plural = "PG 결제 데이터"


class PGDataRefund(models.Model):
    """
    PGDataRefund model for refund
    """
    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE,
                                 related_name='pg_data_refund', verbose_name="주문")
    type = models.CharField(max_length=32, verbose_name="PG 타입",
                            choices=PGDataPayment.PGTypeChoice.choices)
    cancel_memo = models.CharField(max_length=128, verbose_name="PG 취소 메모")
    pg_data_payment = models.ForeignKey("payments.PGDataPayment",
                                        on_delete=models.CASCADE)
    status = models.CharField(max_length=16, verbose_name="PG 상태")
    pg_message = models.CharField(max_length=128, verbose_name="PG 메시지(에러시)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order.order_number}"

    class Meta:
        verbose_name = "PG 환불 데이터"
        verbose_name_plural = "PG 환불 데이터"




