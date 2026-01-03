from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_image', 'quantity', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total', 'status', 'payment_status', 'created_at']
    list_filter = ['status', 'payment_status', 'payment_provider', 'created_at']
    search_fields = ['id', 'user__username', 'transaction_id', 'city', 'country']
    readonly_fields = ['id', 'user', 'total', 'payment_provider', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('id', 'user', 'total', 'status')
        }),
        ('Payment Information', {
            'fields': ('payment_provider', 'payment_status', 'transaction_id')
        }),
        ('Shipping Information', {
            'fields': ('street', 'city', 'state', 'zip_code', 'country')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )
