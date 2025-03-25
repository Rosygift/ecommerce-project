from django.contrib import admin
from .models import CustomUser,Product,ShippingAddress,Category,Wishlist,Cart,CartItem
admin.site.register(CustomUser)
admin.site.register(Product)
admin.site.register(ShippingAddress)
admin.site.register(Category)
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(CartItem)


# Register your models here.
