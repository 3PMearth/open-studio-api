from django.contrib import admin
from .models import Order, OrderToken


# Register your models here.
class OrderTokenInline(admin.TabularInline):
    model = OrderToken
    extra = 3


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_number', 'buyer', 'currency',
                    'sum_price', 'sum_amount', 'country_code',
                    'created_at')
    inlines = [OrderTokenInline]


class OrderTokenAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'token', 'amount', 'price', 'currency')


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderToken, OrderTokenAdmin)

