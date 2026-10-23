from django.contrib import admin
from .models import Product, Category, CategoryType, ProductBatch


@admin.register(ProductBatch)
class ProductBatchAdmin(admin.ModelAdmin):
    list_display  = ('product', 'quantity', 'expiry_date', 'added_by', 'date_added')
    list_filter   = ('expiry_date',)
    search_fields = ('product__name',)



@admin.register(CategoryType)
class CategoryTypeAdmin(admin.ModelAdmin):
    list_display  = ('name', 'color', 'icon')
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'category_type', 'description', 'product_count')
    list_filter   = ('category_type',)
    search_fields = ('name',)

    def product_count(self, obj):
        return obj.products.filter(is_active=True).count()
    product_count.short_description = 'Active Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display    = ('name', 'category', 'quantity', 'status', 'expiry_date', 'is_active', 'last_updated')
    list_filter     = ('category', 'status', 'is_active', 'category__category_type')
    search_fields   = ('name',)
    readonly_fields = ('status', 'date_added', 'last_updated')
