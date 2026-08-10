from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CheckoutForm, ProfileForm, RegisterForm
from .models import Cart, CartItem, Order, OrderItem, Product, Wishlist

def home(request):
    return render(request, 'home.html', {'featured': Product.objects.filter(featured=True)[:8], 'new_arrivals': Product.objects.all()[:4], 'best_sellers': Product.objects.filter(best_seller=True)[:4], 'categories': __import__('store.models', fromlist=['Category']).Category.objects.all()})

def products(request):
    items = Product.objects.select_related('category').all()
    q = request.GET.get('q', '').strip(); category = request.GET.get('category', ''); brand = request.GET.get('brand', ''); sort = request.GET.get('sort', '')
    min_price = request.GET.get('min_price'); max_price = request.GET.get('max_price')
    if q: items = items.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(brand__icontains=q))
    if category: items = items.filter(category__slug=category)
    if brand: items = items.filter(brand__iexact=brand)
    if min_price:
        try: items = items.filter(price__gte=Decimal(min_price))
        except Exception: pass
    if max_price:
        try: items = items.filter(price__lte=Decimal(max_price))
        except Exception: pass
    if sort == 'price_low': items = items.order_by('price')
    elif sort == 'price_high': items = items.order_by('-price')
    elif sort == 'popular': items = items.order_by('-rating')
    return render(request, 'products.html', {'products': items, 'categories': __import__('store.models', fromlist=['Category']).Category.objects.all(), 'brands': Product.objects.exclude(brand='').values_list('brand', flat=True).distinct(), 'q': q})

def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related('category'), slug=slug)
    related = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]
    wished = request.user.is_authenticated and Wishlist.objects.filter(user=request.user, products=product).exists()
    return render(request, 'product_detail.html', {'product': product, 'related': related, 'wished': wished})

def register(request):
    if request.user.is_authenticated: return redirect('home')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save(); messages.success(request, 'Account created. Please sign in.'); return redirect('login')
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated: return redirect('home')
    error = None
    if request.method == 'POST':
        identity = request.POST.get('username', '').strip(); password = request.POST.get('password', '')
        user = authenticate(request, username=identity, password=password)
        if not user:
            candidate = User.objects.filter(email__iexact=identity).first()
            user = authenticate(request, username=candidate.username, password=password) if candidate else None
        if user:
            login(request, user)
            if request.POST.get('remember_me'): request.session.set_expiry(1209600)
            return redirect(request.GET.get('next') or 'home')
        error = 'Invalid username/email or password.'
    return render(request, 'login.html', {'error': error})

def logout_view(request): logout(request); messages.info(request, 'You have been signed out.'); return redirect('home')

@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid(): form.save(); messages.success(request, 'Profile updated.'); return redirect('profile')
    return render(request, 'profile.html', {'form': form, 'recent_orders': request.user.orders.all()[:5]})

@login_required
def change_password(request):
    from django.contrib.auth.forms import PasswordChangeForm
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid(): form.save(); update_session_auth_hash(request, form.user); messages.success(request, 'Password changed.'); return redirect('profile')
    return render(request, 'form_page.html', {'form': form, 'title': 'Change password'})

def _cart(user): return Cart.objects.get_or_create(user=user)[0]
@login_required
def cart(request): return render(request, 'cart.html', {'cart': _cart(request.user)})
@login_required
def add_to_cart(request, product_id):
    if request.method != 'POST': return redirect('product_detail', slug=get_object_or_404(Product, pk=product_id).slug)
    product = get_object_or_404(Product, pk=product_id); quantity = max(1, int(request.POST.get('quantity', 1) or 1)); cart_obj = _cart(request.user)
    item, created = CartItem.objects.get_or_create(cart=cart_obj, product=product, defaults={'quantity': 0})
    if item.quantity + quantity > product.stock_quantity: messages.error(request, f'Only {product.stock_quantity} units are available.')
    else: item.quantity += quantity; item.save(); messages.success(request, f'{product.name} added to cart.')
    return redirect(request.POST.get('next') or 'cart')
@login_required
def update_cart(request, item_id, action):
    item = get_object_or_404(CartItem, pk=item_id, cart__user=request.user)
    if action == 'remove': item.delete()
    elif action == 'increase' and item.quantity < item.product.stock_quantity: item.quantity += 1; item.save()
    elif action == 'decrease':
        if item.quantity == 1: item.delete()
        else: item.quantity -= 1; item.save()
    return redirect('cart')
@login_required
def wishlist(request): return render(request, 'wishlist.html', {'wishlist': Wishlist.objects.get_or_create(user=request.user)[0]})
@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, pk=product_id); wishlist_obj = Wishlist.objects.get_or_create(user=request.user)[0]
    if wishlist_obj.products.filter(pk=product.pk).exists(): wishlist_obj.products.remove(product); messages.info(request, 'Removed from wishlist.')
    else: wishlist_obj.products.add(product); messages.success(request, 'Saved to wishlist.')
    return redirect(request.POST.get('next') or 'wishlist')
@login_required
def checkout(request):
    cart_obj = _cart(request.user)
    if not cart_obj.items.exists(): messages.info(request, 'Your cart is empty.'); return redirect('products')
    form = CheckoutForm(request.POST or None, initial={'name': request.user.get_full_name() or request.user.username, 'email': request.user.email})
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            for item in cart_obj.items.select_related('product'):
                if item.quantity > item.product.stock_quantity: messages.error(request, f'{item.product.name} no longer has enough stock.'); return redirect('cart')
            address = form.save(commit=False); address.user = request.user; address.save()
            order = Order.objects.create(user=request.user, address=address, total_amount=cart_obj.total)
            for item in cart_obj.items.select_related('product'):
                OrderItem.objects.create(order=order, product=item.product, product_name=item.product.name, unit_price=item.product.selling_price, quantity=item.quantity)
                item.product.stock_quantity -= item.quantity; item.product.save(update_fields=['stock_quantity']); item.delete()
        messages.success(request, f'Order {order.order_id} placed successfully. Pay on delivery.'); return redirect('orders')
    return render(request, 'checkout.html', {'form': form, 'cart': cart_obj})
@login_required
def orders(request): return render(request, 'orders.html', {'orders': request.user.orders.prefetch_related('items').all()})
