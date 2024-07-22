from paystackapi.paystack import Paystack
from django.conf import settings

paystack = Paystack(settings.PAYSTACK_SECRET_KEY)
from django.shortcuts import render, redirect
from .models import *
from django.views.generic import *
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.urls import reverse
import paystackapi
import random, string
import logging
from django.core.mail import send_mail
from Vertigo.settings import EMAIL_HOST_USER
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.paginator import Paginator
from django.db import transaction
from django.contrib.auth.decorators import login_required
from functools import wraps


##Customer's Side of the app.

class entry(ListView):
    model = Store
    template_name = 'store/entry.html'


class home(ListView):
    model = product
    template_name = 'store/index.html'

    def get_queryset(self):
        return product.objects.filter(stock__gt=0)


def store_view(request, shop):
    store_n = Store.objects.get(store_name=shop)
    products = product.objects.filter(store=store_n, stock__gt=0)
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'store/shop.html', {'products': products, 'store': store_n, 'page_obj': page_obj})


def perfume_view(request):
    shirts_category = Category.objects.get(cat_name='perfume')
    products = product.objects.filter(category=shirts_category, stock__gt=0)
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'store/perfume.html', {'products': products, 'page_obj': page_obj})


def jewelry_view(request):
    shirts_category = Category.objects.get(cat_name='jewelry')
    products = product.objects.filter(category=shirts_category, stock__gt=0)
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'store/Jewelry.html', {'products': products, 'page_obj': page_obj})


def accessories_view(request):
    shirts_category = Category.objects.get(cat_name='accessories')
    products = product.objects.filter(category=shirts_category, stock__gt=0)
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'store/accessories.html', {'products': products, 'page_obj': page_obj})


def clothing_view(request):
    shirts_category = Category.objects.get(cat_name='clothing')
    products = product.objects.filter(category=shirts_category, stock__gt=0)
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'store/clothing.html', {'products': products, 'page_obj': page_obj})


def product_detail(request, product_id):
    products = product.objects.get(pk=product_id)
    return render(request, 'store/details.html', {'products': products})


def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        products = product.objects.get(pk=product_id)
        if request.method == "POST":
            selected_size = request.POST.get("size") or ''
            existing_cart_item = Cart.objects.filter(user=request.user, product=products, size=selected_size).first()
            if existing_cart_item:
                if existing_cart_item.quantity <= existing_cart_item.product.stock:
                    existing_cart_item.quantity += 1
                    existing_cart_item.save()
                    messages.success(request, "Item quantity updated in cart")
                else:
                    messages.warning(request, "No enough in stock")
            else:
                new_cart_item = Cart(user=request.user, product=products, size=selected_size, quantity=1)
                new_cart_item.save()
                messages.success(request, 'Item has been added to cart')
        return redirect('details', product_id)
    else:
        request.session['add_to_cart_product_id'] = product_id
        request.session['add_to_cart_size'] = request.POST.get("size")
        messages.info(request, 'Please log in to add the item to your cart.')
        return redirect('login')


def cart(request):
    if request.user.is_authenticated:
        carts = Cart.objects.filter(user=request.user)
        return render(request, 'store/cart.html', {'carts': carts})
    else:
        return redirect('login')


def cart_remove(request, cart_item_id):
    kart = get_object_or_404(Cart, pk=cart_item_id)
    kart.delete()
    return redirect('cart_item')


def cart_update(request, cart_item_id):
    kart = get_object_or_404(Cart, pk=cart_item_id)
    if request.method == 'POST':
        new_quantity = int(request.POST.get('quantity'))
        if kart.product.stock >= new_quantity:
            kart.quantity = new_quantity
            kart.save()
        else:
            messages.warning(request, "There is no enough in stock")
    return redirect('cart_item')


def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(
        float(item.product.price.replace(',', '')) * item.quantity for item in cart_items
    )
    delivery_fee = 0.00
    total_price += delivery_fee
    if total_price <= 2500:
        paystack_fee = (1.5 / 100) * total_price
    else:
        paystack_fee = ((1.5 / 100) * total_price) + 100
    total_price += paystack_fee

    if request.method == 'POST':
        order = Order()
        order.user = request.user
        order.name = request.POST['name']
        order.address = request.POST['address']
        order.email = request.POST['email']
        order.telephone = request.POST['telephone']
        order.instructions = request.POST['instructions']
        order.save()
        ref = ''.join(random.choice(string.ascii_lowercase) for i in range(7))
        for cart_item in cart_items:
            order_item = Item(
                stuff=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                size=cart_item.size,
            )
            order_item.save()
        payment_data = {
            "reference": f"{ref}_{order.id}",
            "amount": int(total_price * 100),
            "currency": "NGN",
            "email": order.email,
            "metadata": {"order_id": order.id},
            "callback_url": request.build_absolute_uri(reverse('payment_callback')),
        }
        transaction = paystack.transaction.initialize(**payment_data)
        print(transaction)
        return redirect(transaction['data']['authorization_url'])
    else:
        return render(
            request,
            'store/checkout.html',
            {'cart_items': cart_items, 'total_price': total_price, 'delivery_fee': delivery_fee,
             'paystack_fee': paystack_fee},
        )





def payment_callback(request):
    try:
        reference = request.GET.get('reference')
        verify_transaction = paystackapi.transaction.Transaction.verify(reference)

        # Check if the payment is successful
        if verify_transaction.get('status') == True:
            # Update your order status or perform other actions
            metadata = verify_transaction.get('data', {}).get('metadata', {})
            order_id = metadata.get('order_id')
            if order_id is not None:
                order = get_object_or_404(Order, id=int(order_id))
                order.payment_status = True
                order.save()
                for items in order.order_items.all():
                    product = items.product
                    print(
                        f"Product: {product.name}, Stock before: {product.stock}, Quantity: {items.quantity}")
                    product.stock = product.stock - items.quantity
                    product.save()
                    print(f"Stock after: {product.stock}")  # Debugging statement
                subject = 'Siyu Market Receipt '
                html_message = render_to_string('store/email.html', {'order': order})
                message = strip_tags(html_message)
                recipients = order.get_recipient_list()
                send_mail(subject, message, EMAIL_HOST_USER, recipients, fail_silently=False, html_message=html_message)
                user_cart = Cart.objects.filter(user=request.user)
                user_cart.delete()
                return render(request, "store/email.html", {'order': order})
            else:
                # Handle the case where 'order_id' is not present
                return HttpResponseBadRequest("Invalid request. Missing 'order_id'.")
        else:
            return HttpResponse("Payment failed")
    except KeyError as e:
        # Log the error for debugging purposes
        logging.error(f"KeyError in paystack_callback: {e}")
        return HttpResponseBadRequest("Invalid response from Paystack. Missing expected key.")
    except Exception as e:
        # Log the error for debugging purposes
        logging.error(f"Error in paystack_callback: {e}")
        return HttpResponse("Oops! Something went wrong.")


def search(request):
    s_query = request.GET.get('search')
    products = []
    stores = []
    if s_query:
        products = product.objects.filter(name__icontains=s_query)
        stores = Store.objects.filter(store_name__icontains=s_query)
        total = list(stores) + list(products)

    return render(request, 'store/search.html', {'s_query': s_query, 'products': products, "stores": stores})


# Vendor's Side of the app!

# Register a store
@login_required(login_url='/accounts/login')
def create_store(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            if request.POST["store_name"] and request.POST["description"] and request.POST["store_email"]:
                store = Store()
                store.store_name = request.POST.get("store_name")
                store.description = request.POST.get("description")
                store.email = request.POST.get("store_email")
                store.vendor = request.user

                store.save()
                return redirect("product_list")
            return render(request, "store/create_store.html")
        return render(request, "store/create_store.html")
    return redirect("login")


##Vendor decorator
def store_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'store'):
            return view_func(request, *args, **kwargs)
        else:
            return render(request, "store/forbidden.html")

    return _wrapped_view


# Get all vendors Products
@login_required(login_url='/accounts/login')
@store_required
def product_list(request):
    products = product.objects.filter(store=request.user.store).order_by('name')
    return render(request, 'store/product_list.html', {'products': products})


# Create new product
@login_required(login_url='/accounts/login')
@store_required
def add_product(request):
    if request.method == 'POST':
        if request.POST['name'] and request.POST['price'] and request.FILES['image'] and request.POST['category'] and \
                request.POST['desc'] and request.POST['stock']:
            try:
                cat = request.POST.get('category')
                category = get_object_or_404(Category, cat_name=cat)
                new_product = product()
                new_product.name = request.POST.get('name')
                new_product.price = request.POST.get('price')
                new_product.description = request.POST.get('desc')
                new_product.image = request.FILES['image']
                new_product.category = category
                new_product.store = request.user.store
                new_product.stock = request.POST.get('stock')

                new_product.save()
                return redirect('product_list')
            except Exception as e:
                context = {'error': e.message}
                return render(request, 'store/add_product.html', context)
        context = {'error': 'All fields are required.'}
        return render(request, 'store/add_product.html', context)

    return render(request, 'store/add_product.html')


@login_required(login_url='/accounts/login')
@store_required
def delete_product(request, id):
    try:
        victim = get_object_or_404(product, pk=id)
        victim.delete()

        return redirect('product_list')
    except Exception as e:
        context = {'error': e.message}
        return render(request, 'store/product_list.html', context)


@login_required(login_url='/accounts/login')
@store_required
def update_product(request, id):
    try:
        victim = get_object_or_404(product, pk=id)
        if request.method == 'POST':
            name = request.POST.get('name')
            price = request.POST.get('price')
            desc = request.POST.get('desc')
            image = request.FILES.get('image', None)
            cat = request.POST.get('category')
            stock = request.POST.get('stock')

            if name and price and desc and cat and stock:
                category = get_object_or_404(Category, cat_name=cat)
                victim.name = name
                victim.price = price
                victim.decsription = desc
                victim.stock = stock
                if image:
                    victim.image = image
                victim.category = category

                victim.save()
                return redirect('product_list')
            context = {'error': 'All fields required', 'product': victim, 'categories': Category.objects.all()}
            return render(request, 'store/update_product.html', context)
        context = {'product': victim, 'categories': Category.objects.all()}
        return render(request, 'store/update_product.html', context)
    except Exception as e:
        context = {'error': e.messages, 'product': victim, 'categories': Category.objects.all()}
        return render(request, 'store/update_product.html', context)
