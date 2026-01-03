from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.products.models import Category, Product
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # Create Admin User
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Admin user created (admin/admin123)'))

        # Create Categories
        electronics, _ = Category.objects.get_or_create(name='Electronics', description='Gadgets and devices')
        clothing, _ = Category.objects.get_or_create(name='Clothing', description='Apparel and fashion')
        
        # Subcategories
        phones, _ = Category.objects.get_or_create(name='Smartphones', parent=electronics)
        laptops, _ = Category.objects.get_or_create(name='Laptops', parent=electronics)
        shirts, _ = Category.objects.get_or_create(name='Shirts', parent=clothing)

        self.stdout.write(self.style.SUCCESS('Categories created'))

        # Create Products
        products_data = [
            {
                'name': 'iPhone 15',
                'sku': 'IP15-128',
                'description': 'Latest Apple iPhone',
                'price': 999.99,
                'stock': 50,
                'category': phones
            },
            {
                'name': 'MacBook Pro',
                'sku': 'MBP-M3',
                'description': 'Powerful laptop for pros',
                'price': 1999.99,
                'stock': 20,
                'category': laptops
            },
            {
                'name': 'Cotton T-Shirt',
                'sku': 'TS-WHT-M',
                'description': 'Comfortable white t-shirt',
                'price': 19.99,
                'stock': 100,
                'category': shirts
            }
        ]

        for p_data in products_data:
            if not Product.objects.filter(sku=p_data['sku']).exists():
                Product.objects.create(**p_data)
        
        self.stdout.write(self.style.SUCCESS('Products created'))
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
