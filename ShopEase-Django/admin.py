from django.contrib import admin
from .models import Address, Cart, CartItem, Category, Order, OrderItem, Product, Wishlist

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'selling_price', 'stock_quantity', 'featured', 'best_seller')
    list_filter = ('category', 'featured', 'best_seller', 'brand'); search_fields = ('name', 'brand'); prepopulated_fields = {'slug': ('name',)}
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin): prepopulated_fields = {'slug': ('name',)}
class OrderItemInline(admin.TabularInline): model = OrderItem; extra = 0; readonly_fields = ('product', 'product_name', 'unit_price', 'quantity')
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'user', 'total_amount', 'status', 'payment_status', 'created_at'); list_filter = ('status', 'payment_status'); search_fields = ('order_id', 'user__username'); inlines = [OrderItemInline]
admin.site.register([Address, Cart, CartItem, Wishlist])
