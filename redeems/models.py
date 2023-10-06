from django.db import models

# Create your models here.
class VerifiedTicket(models.Model):
    """
    Verified Ticket List, which has already verified by Verifier
    """
    verifier = models.ForeignKey("redeems.Verifier", on_delete=models.CASCADE,
                                    related_name='verified_tickets', verbose_name="검증자")
    amount = models.IntegerField(verbose_name="수량")
    user_wallet = models.CharField(max_length=128, verbose_name="지갑주소")
    contract_address = models.CharField(max_length=128, verbose_name="컨트랙트 주소")
    nft_id = models.IntegerField(verbose_name="NFT ID")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"verified_ticket : {self.pk}"

    class Meta:
        verbose_name = "검증된 티켓"
        verbose_name_plural = "검증된 티켓"


class Verifier(models.Model):
    """
    Ticket Verifier, who can verify ticket
    """
    verifier_code = models.CharField(max_length=128, verbose_name="검증자 코드")
    contract = models.ForeignKey("contracts.Contract", on_delete=models.CASCADE,
                                    related_name='verifiers', verbose_name="컨트랙트")
    start_time = models.DateTimeField(verbose_name="시작 시간")
    end_time = models.DateTimeField(verbose_name="종료 시간")
    registered = models.BooleanField(default=False, verbose_name="등록 여부")
    active = models.BooleanField(default=True, verbose_name="활성화 여부")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.verifier_code}"

    class Meta:
        verbose_name = "검증자"
        verbose_name_plural = "검증자"

