from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), path('products/', views.products, name='products'), path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('register/', views.register, name='register'), path('login/', views.login_view, name='login'), path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'), path('profile/password/', views.change_password, name='change_password'),
    path('cart/', views.cart, name='cart'), path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'), path('cart/item/<int:item_id>/<str:action>/', views.update_cart, name='update_cart'),
    path('wishlist/', views.wishlist, name='wishlist'), path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('checkout/', views.checkout, name='checkout'), path('orders/', views.orders, name='orders'),
]
