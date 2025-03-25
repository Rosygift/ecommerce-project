from django.urls import path
from .import views
from django.conf.urls.static import static
from django.conf import settings




urlpatterns =[

    path('',views.home,name='home'),
    path('login/',views.login,name='login'),
    path('signup/',views.signup,name='signup'),
    path('search/',views.search,name='search'),
    path('add_shipping_address/',views.add_shipping_address,name='add_shipping_address'),
    path('shipping_address_list/',views.shipping_address_list,name='shipping_address_list'),
    path('category_view/',views.default_category,name='efault_category'),
    path('category_view/<str:food>/',views.category_view,name='category_view'),
    path('wishlist_views/',views.wishlist_views,name='wishlist_views'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart_detail/', views.cart_detail, name='cart_detail'),  # Fixed path
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),  # Fixed path
    path('cart/update/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('payment-success/', views.payment_success, name='payment-success'),
    path('payment-failed/', views.payment_failed, name='payment-failed'),
    path('checkout/<int:product_id>/', views.checkout, name='checkout'),
    path('paypal-ipn/', views.payapal_ipn, name='payapal-ipn'), 
   
    
   

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





https://github.com/Rosygift/ecommerce-project.git