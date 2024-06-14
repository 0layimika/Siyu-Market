from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import auth
from store.models import Cart, product
# Create your views here.
import store.views
import requests


def signup(request):
    if request.method == "POST":
        if request.POST["password"] == request.POST["confirm_password"]:
            try:
                User.objects.get(username=request.POST["username"])
                return render (request, 'accounts/signup.html',{'error':'Email address already exists'})
            except User.DoesNotExist:

                user = User.objects.create_user(request.POST['username'],email=request.POST['username'],password=request.POST['password'])
                auth.login(request, user)
                # next_url = request.GET.get('next')
                add_to_cart_product_id = request.session.get('add_to_cart_product_id')
                add_to_cart_size = request.session.get('add_to_cart_size')
                if add_to_cart_product_id and add_to_cart_size:
                    existing_cart_item = Cart.objects.filter(user=request.user,
                                                             product=product.objects.get(pk=add_to_cart_product_id),
                                                             size=add_to_cart_size).first()
                    if existing_cart_item:
                        # If the same product and size combination already exists in the cart, increase quantity
                        existing_cart_item.quantity += 1
                        existing_cart_item.save()
                    else:
                        # If it's a new product and size combination, create a new cart item
                        new_cart_item = Cart(user=request.user, product=product.objects.get(pk=add_to_cart_product_id),
                                             size=add_to_cart_size, quantity=1)
                        new_cart_item.save()
                    return redirect('cart_item')
                else:
                    return redirect('home')

        else:
            return render(request, 'accounts/signup.html',{'error':'Passwords must match'})
    else:
        return render(request, 'accounts/signup.html')
def login(request):
    if request.method == "POST":
        user = auth.authenticate(username=request.POST["username"],password=request.POST['password'])
        if user is not None:
            auth.login(request, user)
            # next_url = request.GET.get('next')
            add_to_cart_product_id = request.session.get('add_to_cart_product_id')
            add_to_cart_size = request.session.get('add_to_cart_size')
            if add_to_cart_product_id and add_to_cart_size:
                existing_cart_item = Cart.objects.filter(user=request.user, product=product.objects.get(pk=add_to_cart_product_id),
                                                         size=add_to_cart_size).first()
                if existing_cart_item:
                    # If the same product and size combination already exists in the cart, increase quantity
                    existing_cart_item.quantity += 1
                    existing_cart_item.save()
                else:
                    # If it's a new product and size combination, create a new cart item
                    new_cart_item = Cart(user=request.user, product=product.objects.get(pk=add_to_cart_product_id), size=add_to_cart_size, quantity=1)
                    new_cart_item.save()
                return redirect('cart_item')
            else:
                return redirect('home')
        else:
            return render(request,'accounts/login.html',{'error':"Email and Password don't match"})
    else:
        return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    return redirect('home')


