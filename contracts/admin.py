from django.contrib import admin
from .models import Contract, Transaction

# Register your models here.
class ContractAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'symbol', 'contract_address', 'created_at')

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'contract', 'tx_hash', 'to_address', 'gas_price', 'func', 'created_at')


admin.site.register(Contract, ContractAdmin)
admin.site.register(Transaction, TransactionAdmin)
