from .models import Category, Order, Product, Order, OrderItem
from django.contrib import admin

# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'category', 'is_available', 'created_at')
    list_filter = ('is_available', 'category')
    list_editable = ('price', 'stock', 'is_available')
    prepopulated_fields = {'slug': ('name',)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email', 'address', 'city', 'paid', 'created_at']
    list_filter = ['paid', 'created_at']
    inlines = [OrderItemInline]