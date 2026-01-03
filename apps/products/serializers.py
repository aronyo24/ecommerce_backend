from rest_framework import serializers
from .models import Category, Product

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(source='products.count', read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'product_count']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'category', 'category_name', 'name', 'slug', 
            'sku', 'description', 'price', 'stock', 'status', 
            'image', 'createdAt', 'updatedAt'
        ]

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    updatedAt = serializers.DateTimeField(source='updated_at', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'category', 'name', 'slug', 'sku', 
            'description', 'price', 'stock', 'status', 
            'image', 'createdAt', 'updatedAt'
        ]

