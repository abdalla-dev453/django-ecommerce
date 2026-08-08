from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import Category, Product, OrderItem, Profile, Order
from .cart import Cart
from .forms import CartAddProductForm, OrderCreateForm, UserRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.db.models import Q
from django.conf import settings
import stripe
from django.urls import reverse

stripe.api_key = settings.STRIPE_SECRET_KEY


def payment_process(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment_completed'))
        cancel_url = request.build_absolute_uri(reverse('payment_canceled'))

        # Fetch related items safely
        if hasattr(order, 'items'):
            order_items = order.items.all()
        else:
            order_items = order.orderitem_set.all()

        line_items = []
        for item in order_items:
            line_items.append({
                'price_data': {
                    'unit_amount': int(item.price * 100),  # price in cents
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name,
                    },
                },
                'quantity': item.quantity,
            })

        session = stripe.checkout.Session.create(
            mode='payment',
            client_reference_id=order.id,
            success_url=success_url,
            cancel_url=cancel_url,
            line_items=line_items,
        )

        return redirect(session.url, code=330)

    return render(request, 'store/payment_process.html', {
        'order': order,
        'stripe_publishable_key': settings.STRIPE_PUBLISHABLE_KEY,
    })



def payment_completed(request):
    return render(request, 'store/payment_completed.html')

def payment_canceled(request):
    return render(request, 'store/payment_canceled.html')


# view for product list
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)

    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )


    # Filter categories based on the provided category_slug
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Price Range Filters
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'query': query or '',
        'min_price': min_price or '',
        'max_price': max_price or '',
    }
    return render(request, 'store/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    cart_product_form = CartAddProductForm()

    # Optional: fetch related products n the same category
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:3]  # Limit to 3 related products

    context = {
        'product': product,
        'related_products': related_products,
        'cart_product_form': cart_product_form
    }
    return render(request, 'store/product_detail.html', context)


# ---- NEW CART VIEWS ----
@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override']
        )
    return redirect('cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'], 
        'override': True
        })
    return render(request, 'store/cart_detail.html', {'cart': cart})


def order_create(request):
    cart = Cart(request)
    if not cart:
        return redirect('product_list')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            cart.clear()
            return redirect('payment_process', order_id=order.id)
    else:
        form = OrderCreateForm()

    return render(request, 'store/order_create.html', {'cart': cart, 'form': form})


# ----REGISTER VIEWS ----
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save(commit=False)
            new_user.set_password(form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            login(request, new_user)
            return redirect('product_list')
    else:
        form = UserRegistrationForm()
    return render(request, 'store/register.html', {'form': form})


# ---- LOGIN VIEWS ----
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('product_list')
    else:
        form = AuthenticationForm()
    return render(request, 'store/login.html', {'form': form})



# ---- LOGOUT VIEWS ----
def user_logout(request):
    logout(request)
    return redirect('product_list')


# ---PROFILE VIEWS ----
@login_required
def profile(request):
    orders = Order.objects.filter(email=request.user.email)
    return render(request, 'store/profile.html', {'orders': orders})