from django.contrib import admin
from hackserver.regconfirm.models import Registrant

class RegistrantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'confirmed')
    fields = ('name', 'email', 'confirmed', 'secret')
    readonly_fields = ('confirmed', 'secret',)
    list_filter = ('confirmed',)

admin.site.register(Registrant, RegistrantAdmin)
