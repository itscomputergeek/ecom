from django.contrib.sites import requests
from django.shortcuts import render
from .models import Product, Contact, Orders, orderUpdate
from math import ceil
import json
from django.views.decorators.csrf import csrf_exempt
from Paytm import Checksum
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .decorators import check_recaptcha

MERCHANT_KEY = 'GQ#qw6ZMhyDhtK%f'


def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params = {'allProds':allProds}
    return render(request, 'shop/index.html', params)


def about(request):
    return render(request, 'shop/about.html')




def contact(request):
    thank = False
    if request.method=="POST":
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        desc = request.POST.get('desc', '')
        contact = Contact(name=name, email=email, phone=phone, desc=desc)
        contact.save()
        thank = True
    return render(request, 'shop/contact.html', {'thank': thank})


def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = orderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success","updates":updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitems"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')

def searchMatch(query,item):
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    else:
        return False

def search(request):
    query = request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query, item)]

        n = len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        if len(prod)!=0:
            allProds.append([prod, range(1, nSlides), nSlides])
            params = {'allProds': allProds}
            if len(allProds) == 0 or len(query) < 4:
                params = {'msg': "Please make sure to enter relevant search query"}
            return render(request, 'shop/index.html', params)




def productView(request, id):

    # Fetch the product using the id
    product = Product.objects.filter(id=id)
    return render(request, 'shop/prodView.html', {'product':product[0]})

@login_required(login_url="login/")
def checkout(request):
        if request.method=="POST":
            items_json = request.POST.get('itemsJson', '')
            name = request.POST.get('name', '')
            amount = request.POST.get('amount', '')
            email = request.POST.get('email', '')
            address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
            city = request.POST.get('city', '')
            state = request.POST.get('state', '')
            zip_code = request.POST.get('zip_code', '')
            phone = request.POST.get('phone', '')
            order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone, amount=amount)
            order.save()
            update = orderUpdate(order_id=order.order_id, update_desc="The order has been placed")
            update.save()
            thank = True
            id = order.order_id
            param_dict = {
                'MID': 'QhbXeT52515141684458',
                'ORDER_ID': str(order.order_id),
                'TXN_AMOUNT': str(amount),
                'CUST_ID': email,
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'DEFAULT',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',
            }
            param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
            return render(request, 'shop/paytm.html', {'param_dict': param_dict})

        return render(request, 'shop/checkout.html')


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})

def home(request):
    return render(request,'home/home.html')
def handleSignup(request):
    if request.method == 'POST':
       email= request.POST['email']
       Username= request.POST['Username']
       fname= request.POST['fname']
       lname= request.POST['lname']
       pass1= request.POST['pass1']
       pass2= request.POST['pass2']

       if len(Username)> 10:
           messages.success(request, "Username must be under 10 characters")
           return redirect('home')
       if not  Username.isalnum():
           messages.success(request, "Username should only letters")
           return redirect('home')
       if pass1 != pass2 and request.recaptcha_is_valid:
           messages.success(request, "Password doesnt match")
           return redirect('home')

       myuser = User.objects.create_user(Username,email,pass1)
       myuser.first_name = fname
       myuser.last_name=lname
       myuser.save()
       messages.success(request,"Your account has been created")
       return redirect('home')


    else:
        return HttpResponse('404- Not Found')


@check_recaptcha
def handleLogin(request):
    if request.method == 'POST':
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']
        user = authenticate(username=loginusername,password=loginpassword)

        if user is not None and request.recaptcha_is_valid:
            login(request,user)
            messages.success(request,"Sucessfuly login")
            return redirect('home')
        else:
            messages.error(request, "invalid username and password to login")
            return redirect('home')


            return HttpResponse('handleLogin')
    else:
        messages.error(request, "login required to cheakout")
        return redirect('home')


def handleLogout(request):
        logout(request)
        messages.success(request, "Sucessfuly logout")
        return redirect('home')
def cod(request):
    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amount', '')
        email = request.POST.get('email', '')
        address = request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        order = Orders(items_json=items_json, name=name, email=email, address=address, city=city,
                       state=state, zip_code=zip_code, phone=phone, amount=amount)
        order.save()
        update = orderUpdate(order_id=order.order_id, update_desc="The order has been placed")
        update.save()
        thank = True
        id = order.order_id
    return render(request, 'shop/cod.html')


