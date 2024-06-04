from paystackapi.paystack import Paystack
from django.conf import settings
paystack = Paystack(settings.PAYSTACK_SECRET_KEY)
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.views.generic import *
from django.http import HttpResponse, HttpResponseBadRequest
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
# from django.urls import reverse
# Create your views here.

class entry(ListView):
    model = Store
    template_name = 'store/entry.html'

class home(ListView):
    model = product
    template_name = 'store/index.html'

def store_view(request, shop):
    store_n = Store.objects.get(store_name=shop)
    products = product.objects.filter(store=store_n)
    return render(request, 'store/shop.html', {'products': products})

def perfume_view(request):
    shirts_category = Category.objects.get(cat_name='perfume')
    products = product.objects.filter(category=shirts_category)
    return render(request, 'store/perfume.html', {'products': products})

def jewelry_view(request):
    shirts_category = Category.objects.get(cat_name='jewelry')
    products = product.objects.filter(category=shirts_category)
    return render(request, 'store/Jewelry.html', {'products': products})
def accessories_view(request):
    shirts_category = Category.objects.get(cat_name='accessories')
    products = product.objects.filter(category=shirts_category)
    return render(request, 'store/accessories.html', {'products': products})
def clothing_view(request):
    shirts_category = Category.objects.get(cat_name='clothing')
    products = product.objects.filter(category=shirts_category)
    return render(request, 'store/clothing.html', {'products': products})

def product_detail(request, product_id):
    products = product.objects.get(pk=product_id)
    return render(request, 'store/details.html', {'products': products})

def add_to_cart(request, product_id):
    if request.user.is_authenticated:
        products = product.objects.get(pk=product_id)
        if request.method == "POST":
            selected_size = request.POST.get("size")
            existing_cart_item = Cart.objects.filter(user=request.user,product=products, size=selected_size).first()
            if existing_cart_item:
                existing_cart_item.quantity += 1
                existing_cart_item.save()
            else:
                new_cart_item = Cart(user=request.user,product=products, size=selected_size, quantity=1)
                new_cart_item.save()
        return redirect('details',product_id)
    else:
        request.session['add_to_cart_product_id'] = product_id
        request.session['add_to_cart_size'] = request.POST.get("size")
        messages.info(request, 'Please log in to add the item to your cart.')
        return redirect('login')

def cart(request):
    if request.user.is_authenticated:
        carts = Cart.objects.filter(user=request.user)
        return render(request, 'store/cart.html',{'carts':carts})
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
        kart.quantity = new_quantity
        kart.save()
    return redirect('cart_item')

def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(
        float(item.product.price.replace(',', '')) * item.quantity for item in cart_items
    )
    delivery_fee = (12/100)*total_price
    total_price += delivery_fee

    if request.method == 'POST':
        order = Order()
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
            {'cart_items': cart_items, 'total_price': total_price, 'delivery_fee':delivery_fee},
        )

def payment_callback(request):
    try:
        reference = request.GET.get('reference')
        verify_transaction = paystackapi.transaction.Transaction.verify(reference)
        print(verify_transaction)
        # Check if the payment is successful
        if verify_transaction.get('status') == True:
            # Update your order status or perform other actions
            metadata = verify_transaction.get('data', {}).get('metadata', {})
            order_id = metadata.get('order_id')
            if order_id is not None:
                order = get_object_or_404(Order, id=int(order_id))
                order.payment_status = True
                order.save()
                subject = 'Siyu Market Receipt '
                html_message = render_to_string('store/email.html', {'order': order})
                message = strip_tags(html_message)
                recipients = order.get_recipient_list()
                send_mail(subject, message, EMAIL_HOST_USER, recipients, fail_silently=False, html_message=html_message)
                user_cart = Cart.objects.filter(user=request.user)
                user_cart.delete()
                return render(request, "store/email.html", {'order':order})
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
   if s_query:
       products = product.objects.filter(name__icontains=s_query)

   return render(request, 'store/search.html', {'s_query': s_query, 'products': products})

