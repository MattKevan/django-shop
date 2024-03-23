from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from .models import ProductTemplate, Product, Attribute, Option, Variation, generate_variations

class AttributeVariationGenerationTest(TestCase):
    def setUp(self):
        # Initial setup remains the same as in the previous example
        self.product = Product.objects.create(title='Extended Test Product', slug='extended-test-product')
        self.product_template = ProductTemplate.objects.create(title='Extended Test Product Template', slug='extended-test-product-template')

    def create_attribute_with_options(self, title, options_titles):
        attribute = Attribute.objects.create(title=title)
        for option_title in options_titles:
            Option.objects.create(title=option_title, attribute=attribute)
        return attribute

    # Product: Are variations being properly generated when 1 attribute is added?
    def test_product_single_attribute_various_options(self):
        # Test scenario with a single attribute and multiple options
        size_attribute = self.create_attribute_with_options('Size', ['Small', 'Medium', 'Large'])
        self.product.attributes.add(size_attribute)

        generate_variations(self.product)

        expected_combinations_count = 3  # One variation for each size option
        self.assertEqual(Variation.objects.count(), expected_combinations_count)

    # Product template: Are variations being properly generated when 1 attribute is added?
    def test_product_template_single_attribute_various_options(self):
        # Test scenario with a single attribute and multiple options
        size_attribute = self.create_attribute_with_options('Size', ['Small', 'Medium', 'Large'])
        self.product_template.attributes.add(size_attribute)

        generate_variations(self.product_template)

        expected_combinations_count = 3  # One variation for each size option
        self.assertEqual(Variation.objects.count(), expected_combinations_count)

    # Product: Are variations being properly generated when four attributes are added?
    def test_product_four_attributes_various_options(self):
        # Test scenario with four attributes, each having a different number of options
        attributes_options_setup = [
            ('Colour', ['Red', 'Blue']),
            ('Size', ['Small']),
            ('Material', ['Cotton', 'Polyester', 'Silk']),
            ('Style', ['Casual', 'Formal']),
        ]

        for title, options in attributes_options_setup:
            attribute = self.create_attribute_with_options(title, options)
            self.product.attributes.add(attribute)

        generate_variations(self.product)

        # Calculating the expected combinations count (product of options per attribute)
        expected_combinations_count = 2 * 1 * 3 * 2  # 2 Colors, 1 Size, 3 Materials, 2 Styles
        self.assertEqual(Variation.objects.count(), expected_combinations_count)

    # Product template: Are variations being properly generated when four attributes are added?        
    def test_product_template_four_attributes_various_options(self):
        # Test scenario with four attributes, each having a different number of options
        attributes_options_setup = [
            ('Colour', ['Red', 'Blue']),
            ('Size', ['Small']),
            ('Material', ['Cotton', 'Polyester', 'Silk']),
            ('Style', ['Casual', 'Formal']),
        ]

        for title, options in attributes_options_setup:
            attribute = self.create_attribute_with_options(title, options)
            self.product_template.attributes.add(attribute)

        generate_variations(self.product_template)

        # Calculating the expected combinations count (product of options per attribute)
        expected_combinations_count = 2 * 1 * 3 * 2  # 2 Colors, 1 Size, 3 Materials, 2 Styles
        self.assertEqual(Variation.objects.count(), expected_combinations_count)
    
    # Are product templates being properly added to products?    
    def test_adding_product_template_to_product(self):
        size_attribute = self.create_attribute_with_options('Size', ['Small', 'Medium', 'Large'])
        self.product_template.attributes.add(size_attribute)
        
        self.product.product_template = self.product_template
        self.product.save()
        
        updated_product = Product.objects.get(id=self.product.id)
        self.assertEqual(updated_product.product_template.id, self.product_template.id)

        self.assertIn(updated_product, self.product_template.products.all())

def test_template_attributes_added_to_product(self):
    size_attribute = self.create_attribute_with_options('Size', ['Small', 'Medium', 'Large'])
    self.product_template.attributes.add(size_attribute)
    
    self.product.product_template = self.product_template
    self.product.save()
    
    updated_product = Product.objects.get(id=self.product.id)
    self.assertEqual(updated_product.attributes.count(), 1)
    for attribute in self.product_template.attributes.all():
        self.assertIn(attribute, updated_product.attributes.all())

