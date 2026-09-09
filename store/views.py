from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import paytmchecksum
from .models import Product, Order, OrderItem
import uuid
import json

def home(request):
    featured_products = Product.objects.all()[:4]
    return render(request, 'home.html', {'products': featured_products})

def shop(request):
    category = request.GET.get('category')
    if category and category != 'All':
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()
    return render(request, 'shop.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

def customize(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'customize.html', {'product': product})

def get_cart(request):
    return request.session.get('cart', {})

def cart(request):
    cart_data = get_cart(request)
    cart_items = []
    total = 0
    for key, item in cart_data.items():
        try:
            product = Product.objects.get(id=item['product_id'])
            subtotal = product.price * item['quantity']
            total += subtotal
            cart_items.append({
                'key': key,
                'product': product,
                'quantity': item['quantity'],
                'size': item['size'],
                'color': item['color'],
                'custom_text': item.get('custom_text', ''),
                'text_position': item.get('text_position', ''),
                'text_size': item.get('text_size', ''),
                'design': item.get('design', ''),
                'subtotal': subtotal
            })
        except Product.DoesNotExist:
            continue
    
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})

def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))
        size = request.POST.get('size', '')
        color = request.POST.get('color', '')
        
        # customization fields
        custom_text = request.POST.get('custom_text', '')
        text_position = request.POST.get('text_position', '')
        text_size = request.POST.get('text_size', '')
        design = request.POST.get('design', '')

        cart_data = get_cart(request)
        
        # generate a unique key for the cart item since customizations can vary
        item_key = str(uuid.uuid4())
        
        cart_data[item_key] = {
            'product_id': product.id,
            'quantity': quantity,
            'size': size,
            'color': color,
            'custom_text': custom_text,
            'text_position': text_position,
            'text_size': text_size,
            'design': design
        }
        
        request.session['cart'] = cart_data
        messages.success(request, 'Item added to cart.')
        return redirect('cart')
    return redirect('shop')

def remove_from_cart(request, item_key):
    cart_data = get_cart(request)
    if item_key in cart_data:
        del cart_data[item_key]
        request.session['cart'] = cart_data
        messages.success(request, 'Item removed from cart.')
    return redirect('cart')

def checkout(request):
    cart_data = get_cart(request)
    if not cart_data:
        messages.warning(request, 'Your cart is empty.')
        return redirect('shop')

    total = sum([Product.objects.get(id=item['product_id']).price * item['quantity'] for item in cart_data.values() if Product.objects.filter(id=item['product_id']).exists()])

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')
        
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
            total_price=total,
            status='Pending'
        )
        
        # generate unique paytm order id
        order.paytm_order_id = f"ORDER_{order.id}_{uuid.uuid4().hex[:8]}"
        order.save()
        
        for key, item in cart_data.items():
            try:
                product = Product.objects.get(id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    size=item['size'],
                    color=item['color'],
                    custom_text=item.get('custom_text', ''),
                    text_position=item.get('text_position', ''),
                    text_size=item.get('text_size', ''),
                    design=item.get('design', '')
                )
            except Product.DoesNotExist:
                pass
                
        # prepare Paytm parameters
        paytm_dict = {
            'MID': settings.PAYTM_MERCHANT_ID,
            'ORDER_ID': order.paytm_order_id,
            'TXN_AMOUNT': str(total),
            'CUST_ID': f"CUST_{order.id}",
            'INDUSTRY_TYPE_ID': settings.PAYTM_INDUSTRY_TYPE_ID,
            'WEBSITE': settings.PAYTM_WEBSITE,
            'CHANNEL_ID': settings.PAYTM_CHANNEL_ID,
            'CALLBACK_URL': request.build_absolute_uri('/payment/verify/'),
        }
        
        paytm_dict['CHECKSUMHASH'] = paytmchecksum.generateSignature(paytm_dict, settings.PAYTM_MERCHANT_KEY)
        
        # We don't clear cart here yet, we can clear it on success
        return render(request, 'paytm_form.html', {
            'paytm_dict': paytm_dict,
            'paytm_environment': settings.PAYTM_ENVIRONMENT
        })
        
    return render(request, 'checkout.html', {'total': total})

@csrf_exempt
def payment_verify(request):
    if request.method == 'POST':
        data_dict = {}
        for key in request.POST:
            data_dict[key] = request.POST[key]
            
        checksum = data_dict.pop('CHECKSUMHASH', '')
        
        # Verify the signature
        verify = False
        if checksum:
            try:
                verify = paytmchecksum.verifySignature(data_dict, settings.PAYTM_MERCHANT_KEY, checksum)
            except Exception:
                verify = False
        
        if verify:
            if data_dict.get('RESPCODE') == '01':
                paytm_order_id = data_dict.get('ORDERID')
                try:
                    order = Order.objects.get(paytm_order_id=paytm_order_id)
                    order.is_paid = True
                    order.paytm_transaction_id = data_dict.get('TXNID')
                    order.status = 'Processing'
                    order.save()
                    
                    request.session['cart'] = {}
                    return redirect('order_success', order_id=order.id)
                except Order.DoesNotExist:
                    messages.error(request, 'Order not found.')
                    return redirect('shop')
            else:
                messages.error(request, f"Payment failed. Reason: {data_dict.get('RESPMSG')}")
                return redirect('cart')
        else:
            paytm_msg = data_dict.get('RESPMSG')
            if paytm_msg:
                messages.error(request, f"Paytm error: {paytm_msg} (Check your API keys)")
            else:
                messages.error(request, 'Payment signature verification failed.')
            return redirect('cart')
            
    return redirect('home')

def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order_success.html', {'order': order})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        return redirect('home')

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': orders})
