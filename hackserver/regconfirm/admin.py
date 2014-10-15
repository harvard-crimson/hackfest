from django.contrib import admin
from hackserver.regconfirm.models import Registrant

class RegistrantAdmin(admin.ModelAdmin):
    readonly_fields = ('secret',)
    list_filter = ('confirmed',)

admin.site.register(Registrant, RegistrantAdmin)
