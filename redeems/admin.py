from django.contrib import admin
from .models import VerifiedTicket, Verifier

# Register your models here.
class VerifiedTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'nft_id', 'verifier', 'user_wallet', 'amount')

class VerifierAdmin(admin.ModelAdmin):
    list_display = ('id', 'verifier_code', 'contract', 'active')


admin.site.register(VerifiedTicket, VerifiedTicketAdmin)
admin.site.register(Verifier, VerifierAdmin)
