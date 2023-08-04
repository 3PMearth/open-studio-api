from django.db import models
from utils.common import upload_file_to_s3

# Create your models here.
class Contract(models.Model):
    class ContractTypeChoice(models.TextChoices):
        MUSIC = 'MUSIC', 'MUSIC'
        TICKET = 'TICKET', 'TICKET'

    name = models.CharField(max_length=128, verbose_name="이름")
    symbol = models.CharField(max_length=32, verbose_name="심볼")
    cover_img = models.ImageField(upload_to=upload_file_to_s3,
                                  null=True, blank=True, verbose_name="커버 이미지")
    contract_address = models.CharField(max_length=128, verbose_name="컨트랙트 주소")
    description_ko = models.TextField(verbose_name="설명(한글)")
    description_en = models.TextField(verbose_name="설명(영어)")
    slug = models.SlugField(max_length=128, verbose_name="슬러그")
    type = models.CharField(max_length=32, choices=ContractTypeChoice.choices,
                            verbose_name="컨트랙트 타입")
    active = models.BooleanField(default=True, verbose_name="활성화 여부")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "컨트랙트"
        verbose_name_plural = "컨트랙트"


# transaction history
class Transaction(models.Model):
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE,
                                 related_name='transactions', verbose_name="컨트랙트")
    tx_hash = models.CharField(max_length=128, verbose_name="트랜잭션 해시")
    from_address = models.CharField(max_length=128, verbose_name="보내는 주소(서명주체)")
    to_address = models.CharField(max_length=128, verbose_name="받는 주소", null=True, blank=True)
    amount = models.IntegerField(verbose_name="수량", null=True, blank=True)
    gas_used = models.IntegerField(verbose_name="사용된 가스", null=True, blank=True)
    gas_price = models.IntegerField(verbose_name="가스 가격(gwei)", null=True, blank=True)
    status = models.IntegerField(verbose_name="상태", null=True, blank=True)
    nonce = models.IntegerField(verbose_name="nonce", default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.tx_hash}"

    class Meta:
        verbose_name = "트랜잭션"
        verbose_name_plural = "트랜잭션"