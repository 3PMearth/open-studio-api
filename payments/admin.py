from django.contrib import admin
from .models import PGDataPayment, PGDataRefund


# Register your models here.
class PGDataPaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'type', 'status', 'vid',
                    'method_type', 'created_at')


class PGDataRefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'type', 'cancel_memo',
                    'status', 'created_at')


admin.site.register(PGDataPayment, PGDataPaymentAdmin)
admin.site.register(PGDataRefund, PGDataRefundAdmin)
