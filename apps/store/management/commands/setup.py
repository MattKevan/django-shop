from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from apps.store.models import StoreConfiguration

class Command(BaseCommand):
    help = 'Creates groups, assigns permissions, and creates store configuration'

    def handle(self, *args, **options):
        self.create_groups_and_assign_permissions()
        self.create_store_configuration()
        self.stdout.write(self.style.SUCCESS('Groups and permissions created successfully.'))

    def create_groups_and_assign_permissions(self):
        # Create StoreOwner group and assign permissions
        store_owner_group, created = Group.objects.get_or_create(name='StoreOwner')
        store_owner_permissions = [
            ('store', 'storeconfiguration', 'change_storeconfiguration'),
            ('store', 'storeconfiguration', 'view_storeconfiguration'),
            ('store', 'shop', 'add_shop'),
            ('store', 'shop', 'change_shop'),
            ('store', 'shop', 'delete_shop'),
            ('store', 'shop', 'view_shop'),
            ('products', 'product', 'add_product'),
            ('products', 'product', 'change_product'),
            ('products', 'product', 'delete_product'),
            ('products', 'product', 'view_product'),
            ('orders', 'order', 'add_order'),
            ('orders', 'order', 'change_order'),
            ('orders', 'order', 'delete_order'),
            ('orders', 'order', 'view_order'),
        ]
        self.assign_permissions(store_owner_group, store_owner_permissions)

        # Create ShopOwner group and assign permissions
        shop_owner_group, created = Group.objects.get_or_create(name='ShopOwner')
        shop_owner_permissions = [
            ('store', 'shop', 'add_shop'),
            ('store', 'shop', 'change_shop'),
            ('store', 'shop', 'delete_shop'),
            ('store', 'shop', 'view_shop'),
            ('products', 'product', 'add_product'),
            ('products', 'product', 'change_product'),
            ('products', 'product', 'delete_product'),
            ('products', 'product', 'view_product'),
            ('orders', 'order', 'add_order'),
            ('orders', 'order', 'change_order'),
            ('orders', 'order', 'delete_order'),
            ('orders', 'order', 'view_order'),
        ]
        self.assign_permissions(shop_owner_group, shop_owner_permissions)

        # Create ShopMember group and assign permissions
        shop_member_group, created = Group.objects.get_or_create(name='ShopMember')
        shop_member_permissions = [
            ('store', 'shop', 'change_shop'),
            ('products', 'product', 'add_product'),
            ('products', 'product', 'change_product'),
            ('products', 'product', 'delete_product'),
            ('products', 'product', 'view_product'),
            ('orders', 'order', 'add_order'),
            ('orders', 'order', 'change_order'),
            ('orders', 'order', 'delete_order'),
            ('orders', 'order', 'view_order'),
        ]
        self.assign_permissions(shop_member_group, shop_member_permissions)

    def assign_permissions(self, group, permissions):
        for app_label, model_name, codename in permissions:
            content_type = ContentType.objects.get(app_label=app_label, model=model_name)
            permission = Permission.objects.get(content_type=content_type, codename=codename)
            group.permissions.add(permission)

    def create_store_configuration(self):
        if not StoreConfiguration.objects.exists():
            StoreConfiguration.objects.create()
            