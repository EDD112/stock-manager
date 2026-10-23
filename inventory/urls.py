from django.urls import path
from . import views

urlpatterns = [
    # Products
    path('',                         views.product_list,       name='product_list'),
    path('add/',                     views.product_add,        name='product_add'),
    path('<int:pk>/edit/',           views.product_edit,       name='product_edit'),
    path('<int:pk>/deactivate/',     views.product_deactivate, name='product_deactivate'),
    path('<int:pk>/restore/',        views.product_restore,         name='product_restore'),
    path('<int:pk>/restore/confirm/', views.product_restore_confirm, name='product_restore_confirm'),
    path('<int:pk>/detail/',         views.product_detail,     name='product_detail'),
    path('<int:pk>/stock/',          views.stock_movement,     name='stock_movement'),
    path('<int:pk>/add-stock/',      views.add_stock,          name='add_stock'),
    path('<int:pk>/remove-stock/',   views.remove_stock,       name='remove_stock'),
    path('<int:product_pk>/batch/<int:batch_pk>/edit/', views.batch_edit, name='batch_edit'),
    path('inactive/',                views.inactive_products,         name='inactive_products'),
    path('inactive/clear/',          views.clear_inactive_products,   name='clear_inactive_products'),
    path('search/',                          views.live_search,                        name='live_search'),
    path('search/inactive/',                 views.live_search_inactive_products,     name='live_search_inactive_products'),
    path('categories/search/',               views.live_search_categories,            name='live_search_categories'),
    path('categories/search/inactive/',      views.live_search_inactive_categories,   name='live_search_inactive_categories'),
    # Categories
    # Categories
    path('categories/',                        views.category_list,            name='category_list'),
    path('categories/add/',                    views.category_add,             name='category_add'),
    path('categories/inactive/',               views.inactive_categories,      name='inactive_categories'),
    path('categories/inactive/clear/',         views.clear_inactive_categories, name='clear_inactive_categories'),
    path('categories/<int:pk>/edit/',          views.category_edit,            name='category_edit'),
    path('categories/<int:pk>/delete/',        views.category_delete,          name='category_delete'),
    path('categories/<int:pk>/restore/',       views.category_restore,         name='category_restore'),
    path('categories/<int:pk>/restore/confirm/', views.category_restore_confirm, name='category_restore_confirm'),
    # Category Types (custom)
    path('category-types/',                      views.category_type_list,   name='category_type_list'),
    path('category-types/add/',                  views.category_type_add,    name='category_type_add'),
    path('category-types/<int:pk>/edit/',        views.category_type_edit,   name='category_type_edit'),
    path('category-types/<int:pk>/delete/',      views.category_type_delete, name='category_type_delete'),
    # Exports
    path('export/excel/',                views.export_inventory_excel,   name='export_inventory_excel'),
    path('export/pdf/',                  views.export_inventory_pdf,     name='export_inventory_pdf'),
    path('export/expiration/excel/',     views.export_expiration_excel,  name='export_expiration_excel'),
    path('export/expiration/pdf/',       views.export_expiration_pdf,    name='export_expiration_pdf'),
]
