from django.contrib import admin
from .models import StoreConfiguration, Shop


class StoreAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Disable adding new instances
        return False

    def has_delete_permission(self, request, obj=None):
        # Disable deleting instances
        return False

    def has_change_permission(self, request, obj=None):
        # Allow editing only for superusers and members of the StoreAdmin group
        return request.user.is_superuser or request.user.groups.filter(name='StoreAdmin').exists()

admin.site.register(StoreConfiguration, StoreAdmin)
admin.site.register(Shop)