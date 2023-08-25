from django.db import models
from utils.common import upload_file_to_s3

# Create your models here.

class User(models.Model):
    wallet_address = models.CharField(max_length=128, verbose_name="지갑주소", unique=True)
    phone_number = models.CharField(max_length=64, verbose_name="전화번호",
                                    null=True, blank=True)
    country_code = models.CharField(max_length=16, verbose_name="국가코드",
                                    null=True, blank=True)
    email = models.CharField(max_length=128, verbose_name="이메일",
                             null=True, blank=True)
    first_name = models.CharField(max_length=64, verbose_name="이름",
                                    null=True, blank=True)
    last_name = models.CharField(max_length=64, verbose_name="성",
                                    null=True, blank=True)
    sso_type = models.CharField(max_length=16, verbose_name="SSO 타입")
    slug = models.CharField(max_length=32, verbose_name="슬러그", null=True, blank=True)

    info = models.TextField(verbose_name="추가정보", null=True, blank=True)
    profile_img = models.ImageField(upload_to=upload_file_to_s3,
                                    null=True, blank=True, verbose_name="프로필 이미지")

    def __str__(self):
        return f"[{self.id}] {self.email}"

    class Meta:
        verbose_name = "사용자"
        verbose_name_plural = "사용자"
