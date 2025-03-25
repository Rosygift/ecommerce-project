from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, authenticate
from .forms import RegistrationForm, SearchForm, ShippingAddressForm, WishlistForm
from .models import Product, ShippingAddress, Category, Wishlist, Cart, CartItem
from django.contrib import messages
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings
import uuid
from django.http import HttpResponse
from django.urls import reverse

def home(request):
    products = Product.objects.all()  # Corrected to use 'Product' with uppercase 'P'
    return render(request, 'home.html', {'products': products})  # Corrected context key

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def signup(request):
    """Views to handle user registration"""
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            auth_login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'signup.html', {'form': form})

def search(request):
    form = SearchForm(request.GET or None)
    query = None
    results = []

    if form.is_valid():
        query = form.cleaned_data.get('query')
        if query:
            results = Product.objects.filter(name__icontains=query)  # Corrected lookup

    return render(request, 'search.html', {'form': form, 'query': query, 'results': results})

def add_shipping_address(request):
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            shipping_address = form.save(commit=False)
            shipping_address.user = request.user
            shipping_address.save()
            return redirect('shipping_address_list')
    else:
        form = ShippingAddressForm()

    return render(request, 'add_shipping_address.html', {'form': form})

def shipping_address_list(request):
    addresses = ShippingAddress.objects.filter(user=request.user)  # Corrected model reference
    return render(request, 'shipping_address_list.html', {'addresses': addresses})  # Corrected context key

def default_category(request):
    return render(request, 'category.html', {'category': None, 'products': []})

def category_view(request, food):
    food = food.replace('_', ' ')  # Replacing underscores with spaces if necessary

    try:
        category = Category.objects.get(name=food)  # Corrected to use 'Category.objects.get()'
        products = Product.objects.filter(category=category)  # Corrected 'Product' to use uppercase
        return render(request, "category.html", {'category': category, 'products': products})
    except Category.DoesNotExist:
        messages.error(request, 'That category does not exist.')
        return redirect('home')

def wishlist_views(request):
    # Get or create a wishlist for the logged-in user
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = WishlistForm(request.POST, instance=wishlist)
        if form.is_valid():
            form.save()  # Save the updated wishlist data
            return redirect('home')  # Redirect to the 'wishlist' URL after success
    else:
        form = WishlistForm(instance=wishlist)

    return render(request, 'wishlist.html', {'form': form, 'wishlist': wishlist})

# Add product to the cart
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)  # Get the product
    cart, created = Cart.objects.get_or_create(user=request.user)  # Get or create the user's cart

    # Get or create the cart item, ensuring it is associated with the correct cart and product
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1  # Increment quantity if item already exists in cart
        cart_item.save()

    return redirect('cart_detail')  # Redirect to cart detail page

# Display cart details
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)  # Get or create the user's cart
    cart_items = cart.items.all()  # Retrieve all items related to the cart
    total_price = sum(item.get_total_price() for item in cart_items)  # Calculate total price

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }

    return render(request, 'cart.html', context)  # Return cart details to the template

# Remove an item from the cart
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)  # Get cart item
    cart_item.delete()  # Remove the CartItem from the cart
    return redirect('cart_detail')  # Redirect to cart detail page

# Update the quantity of a cart item
def update_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)  # Get cart item

    if request.method == 'POST':
        quantity = int(request.POST.get("quantity", 1))  # Get quantity from POST data (default to 1)
        cart_item.quantity = max(1, quantity)  # Ensure quantity is at least 1
        cart_item.save()

    return redirect('cart_detail')  # Redirect to cart detail page
def payapal_ipn(request):
    return HttpResponse('paypal ipn endpoint')

def payment_notification(sender, **kwargs):
    """handles paypal payment notifications."""
    ipn_obj = sender
    if ipn_obj.payment_status == 'Completed':
        if ipn_obj.receiver_email != settings.PAYPAL_RECIEVER_EMAIL:
            return
        try:
            cart = Cart.objects.get(user=request.user)
            cart.is_paid = True
            cart.save()
        except Cart.DoesNotExist:
            pass

def payment_success(request):
    """view to display payment success."""
    return render(request, 'payment_success.html')

def payment_failed(request):
    """view to display payment failure."""
    return render(request, 'payment_failed.html')

def checkout(request, product_id):
    """views to handle checkout process."""
    product = get_object_or_404(Product, id=product_id)
    host = request.get_host()
    total_price = request.GET.get('total_price', product.price)

    paypal_checkout = {
        'business': settings.PAYPAL_RECIEVER_EMAIL,
        'amount': total_price,
        'item_name': product.name,
        'invoice': str(uuid.uuid4()),
        'currency_code': 'USD',
        'notify_url': f"http://{host}{reverse('payapal-ipn')}",
        'return_url': f"http://{host}{reverse('payment-success')}",
        'cancel_url': f"http://{host}{reverse('payment-failed')}",
    }
    paypal_payment = PayPalPaymentsForm(initial=paypal_checkout)
    context = {
        'product': product,
        'total_price': total_price,
        'paypal': paypal_payment
    }
    return render(request, 'checkout.html', context)
