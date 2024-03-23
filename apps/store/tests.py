from django.test import TestCase
from django.db.models.signals import post_migrate
from django.apps import apps
from .models import StoreConfiguration, Shop
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.db import IntegrityError
from django.core.exceptions import ValidationError

class StoreConfigurationTestCase(TestCase):
    
    def setUp(self):
        # Create a superuser for testing
        self.superuser = get_user_model().objects.create_superuser(
            username='testadmin',
            email='testadmin@example.com',
            password='testpassword'
        )
        call_command('setup')
            
    def test_store_owner_group_created(self):
        # Assert that the StoreOwner group is created
        self.assertTrue(Group.objects.filter(name='StoreOwner').exists())

    def test_shop_owner_group_created(self):
        # Assert that the ShopOwner group is created
        self.assertTrue(Group.objects.filter(name='ShopOwner').exists())

    def test_shop_member_group_created(self):
        # Assert that the ShopMember group is created
        self.assertTrue(Group.objects.filter(name='ShopMember').exists())

    # TODO Add tests for permissions
    
    #
    # Store configuration
    #
    
    def test_storeconfig_created(self):
        # Assert that the StoreConfiguration content item has been created
        self.assertEqual(StoreConfiguration.objects.count(), 1)

    def test_storeconfig_properly_set_up(self):
        #Assert the StoreConfiguration item has been created properly
        
        store_config = StoreConfiguration.objects.first()
        self.assertEqual(store_config.name,"My shop")
        #self.assertEqual(store_config.store_admin, self.superuser)
    
    def test_create_single_store_configuration(self):
        # Assert that no more than 1 storeconfiguration objects can be created
        
        # Delete any store configuration objects
        StoreConfiguration.objects.all().delete()
        
        # Create the first store configuration object
        store_config1 = StoreConfiguration.objects.create(
            name='Store Configuration 1',
        )
        
        # Assert that the first store configuration object was created successfully
        self.assertEqual(StoreConfiguration.objects.count(), 1)
        
        with self.assertRaises(ValueError):
            store_config2 = StoreConfiguration.objects.create(
                name='Store Configuration 2',
                # Set other fields as needed
            )
        
        # Assert that only one store configuration object exists in the database
        self.assertEqual(StoreConfiguration.objects.count(), 1)
        
        # Assert that the existing store configuration object is the first one created
        self.assertEqual(StoreConfiguration.objects.first(), store_config1)
