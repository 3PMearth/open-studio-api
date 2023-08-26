from django.contrib import admin
from .models import Token, Asset


# Register your models here.
class AssetInline(admin.TabularInline):
    model = Asset
    extra = 3


class TokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contract', 'user',
                    'price_krw', 'price_usd', 'nft_id',
                    'stock', 'status', 'created_at')
    inlines = [AssetInline]


class AssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'token', 'name', 'type')


admin.site.register(Token, TokenAdmin)
admin.site.register(Asset, AssetAdmin)
