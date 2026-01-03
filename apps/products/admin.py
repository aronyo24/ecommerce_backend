from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'product_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock', 'status', 'sku', 'created_at')
    list_filter = ('status', 'category', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'sku', 'description')
    list_editable = ('price', 'stock', 'status')
    readonly_fields = ('created_at', 'updated_at')
