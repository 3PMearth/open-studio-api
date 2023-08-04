from django.db import models
from utils.common import upload_file_to_s3
from users.models import User
from django.conf import settings
from contracts.models import Contract

class Token(models.Model):
    """
    token model, ERC1155 token
    """
    class TokenStatusChoice(models.TextChoices):
        PREPARE = 'PREPARE', 'DB만 저장'
        MINTED = 'MINTED', '실제 minting됨'
        ERROR = 'ERROR', 'minting error'
        BURN = 'BURN', 'burn 됨'
        CANCEL = 'CANCEL', '취소됨'

    name = models.CharField(max_length=128, verbose_name="이름")
    token_img = models.ImageField(upload_to=upload_file_to_s3,
                                    null=True, blank=True, verbose_name="토큰 이미지")
    animation = models.FileField(upload_to=upload_file_to_s3,
                                    null=True, blank=True, verbose_name="애니메이션")
    contract = models.ForeignKey(Contract, related_name='contract', on_delete=models.CASCADE,
                                    verbose_name="컨트랙트")
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='user', verbose_name="사용자(creator)")
    nft_id = models.IntegerField(verbose_name="NFT ID", null=True, blank=True)
    stock = models.IntegerField(verbose_name="재고(amount)", default=1)
    price_krw = models.CharField(max_length=32, verbose_name="가격(KRW)")
    price_usd = models.CharField(max_length=32, verbose_name="가격(USD)")
    description_ko = models.TextField(verbose_name="설명(한글)")
    description_en = models.TextField(verbose_name="설명(영어)")
    status = models.CharField(max_length=32, verbose_name="상태", choices=TokenStatusChoice.choices,
                                default=TokenStatusChoice.PREPARE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}({self.nft_id})"

    class Meta:
        verbose_name = "토큰"
        verbose_name_plural = "토큰"



class Asset(models.Model):
    class AssetTypeChoice(models.TextChoices):
        IMAGE = 'image', 'image'
        MUSIC = 'music/mp3', 'music/mp3'
        FILE = 'file', 'file'
        VIDEO = 'video', 'video'
        OTHER = 'etc', 'etc'

    name = models.CharField(max_length=128, verbose_name="에셋이름")
    type = models.CharField(max_length=128, choices=AssetTypeChoice.choices,
                            verbose_name="에셋타입")
    media = models.FileField(upload_to=upload_file_to_s3, verbose_name="에셋 실제파일")
    download = models.BooleanField(default=False, verbose_name="다운로드 가능여부")
    token = models.ForeignKey(Token, on_delete=models.CASCADE,
                              related_name='assets', null=True, blank=True,
                              verbose_name="토큰")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name}({self.type})"

    class Meta:
        verbose_name = "에셋"
        verbose_name_plural = "에셋"




