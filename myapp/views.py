from django.shortcuts import render,HttpResponseRedirect
from django.contrib.messages import success,error
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator

import razorpay

from django.conf import settings
from django.core.mail import send_mail
from random import randint


from .models import *


# Create your views here.
def index(request):
    products=Product.objects.all().order_by("id")[0:12]
    testimonials = Testimonial.objects.all().order_by("-id")
    return render(request,"index.html",{"products":products,'testimonials':testimonials})

def about(request):
    return render(request,"about.html")



def addToCart(Request):
    if(Request.method=="POST"):
        cart = Request.session.get('cart',None)
        qty = int(Request.POST.get("qty"))
        id = Request.POST.get("id")
        try:
            p = Product.objects.get(id=id)
            if(cart):
                if(str(id) in cart.keys()):
                    item = cart[str(id)]
                    item['qty'] = item['qty']+qty
                    item['total'] = item['total']+qty*item['price']
                    cart[str(id)] = item
                else:
                    cart.setdefault(str(id),{'productid':id,'name':p.name,'brand':p.brand.name,'color':p.color,'size':p.size,'price':p.finalprice,'qty':qty,'total':qty*p.finalprice,'pic':p.pic1.url})
            else:               
                cart = {str(id):{'productid':id,'name':p.name,'brand':p.brand.name,'color':p.color,'size':p.size,'price':p.finalprice,'qty':qty,'total':qty*p.finalprice,'pic':p.pic1.url}}
    
            Request.session['cart'] = cart
            Request.session.set_expiry(60*60*24*30)
        except:
            pass
    return HttpResponseRedirect("/cart/")
def cart(Request):
    cart = Request.session.get('cart',None)
    subtotal = 0
    shipping = 0
    total = 0
    if(cart):
        for value in cart.values():
            subtotal = subtotal + value['total']
        if(subtotal>0 and subtotal<1000):
            shipping = 150
        total = subtotal+shipping
    return render(Request,"cart.html",{'cart':cart,'subtotal':subtotal,'shipping':shipping,'total':total})

def deleteCart(Request,id):
    cart = Request.session.get("cart",None)
    if(cart):
        del cart[id]
        Request.session['cart']=cart
    else:
        pass
    return HttpResponseRedirect("/cart/")

def updateCart(Request,id,op):
    cart = Request.session.get("cart",None)
    if(cart):
        item = cart[id]
        if(op=="dec" and item['qty']==1):
            return HttpResponseRedirect("/cart/")
        else:
            if(op=="dec"):
                item['qty'] = item['qty']-1
                item['total'] = item['total']-item['price']
            else:
                item['qty'] = item['qty']+1
                item['total'] = item['total']+item['price']
        cart[id]=item
        Request.session['cart']=cart
    else:
        pass
    return HttpResponseRedirect("/cart/")



def contact(request):
    if(request.method=="POST"):
        c = Contact()
        c.name = request.POST.get("name")
        c.email = request.POST.get("email")
        c.phone = request.POST.get("phone")
        c.subject = request.POST.get("subject")
        c.message = request.POST.get("message")
        c.save()
        success(request,"Thanks to Share Your Query With US!!! Our Team Will Contact You Soon!!!")
    return render(request,"contact.html")


def singleproduct(request,id):
    product=Product.objects.get(id=id)
    return render(request,"single-product.html",{"product":product})



def shop(Request,mc,sc,br):
    if(mc=="All" and sc=="All" and br=="All"):
        products = Product.objects.all().order_by("-id")
    elif(mc!="All" and sc=="All" and br=="All"):
        products = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc)).order_by("-id")
    elif(mc=="All" and sc!="All" and br=="All"):
        products = Product.objects.filter(subcategory=Subcategory.objects.get(name=sc)).order_by("-id")
    elif(mc=="All" and sc=="All" and br!="All"):
        products = Product.objects.filter(brand=Brand.objects.get(name=br)).order_by("-id")
    elif(mc!="All" and sc!="All" and br=="All"):
        products = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc),subcategory=Subcategory.objects.get(name=sc)).order_by("-id").order_by("-id")
    elif(mc!="All" and sc=="All" and br!="All"):
        products = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc),brand=Brand.objects.get(name=br)).order_by("-id").order_by("-id")
    elif(mc=="All" and sc!="All" and br!="All"):
        products = Product.objects.filter(brand=Brand.objects.get(name=br),subcategory=Subcategory.objects.get(name=sc)).order_by("-id").order_by("-id")    
    else:
        products = Product.objects.filter(maincategory=Maincategory.objects.get(name=mc),subcategory=Subcategory.objects.get(name=sc),brand=Brand.objects.get(name=br)).order_by("-id").order_by("-id")    
    
    
    maincategory = Maincategory.objects.all().order_by("-id")
    subcategory = Subcategory.objects.all().order_by("-id")
    brand = Brand.objects.all().order_by("-id")

    paginator = Paginator(products, 12)
    page_number = Request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(Request,"shop.html",{'maincategory':maincategory,'subcategory':subcategory,'brand':brand,'mc':mc,'sc':sc,'br':br,'page_obj':page_obj})

def login(request):
    if(request.method=="POST"):
       username= request.POST.get("username")
       password= request.POST.get("password")
       user= authenticate(username=username,password=password)
       if(user is not None):
          auth_login(request, user)
          if(user.is_superuser):
             return HttpResponseRedirect("/admin/")
          else:
             return HttpResponseRedirect("/profile/")
       else:
          error(request,"Invalid Username and Password!!!")
    return render(request,"login.html")


def forgetPassword1(Request):
    if(Request.method=="POST"):
        username = Request.POST.get("username")
        try:
            buyer = Buyer.objects.get(username=username)
            otp = randint(100000,999999)
            buyer.otp = otp
            buyer.save()

            subject = 'OTP for Password Reset!! team -: SuperShop'
            message = """
                        Hello """+buyer.name+"""
                        OTP for Password Reset Is """+str(otp)+"""
                        Please Never Share Your OTP With AnyOne
                      """
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [buyer.email, ]
            send_mail( subject, message, email_from, recipient_list )
            Request.session['reset-password-user'] = buyer.username
            return HttpResponseRedirect("/forget-password-2/")
        except:
            error(Request,"User Name Not Found in Our Data Record!!!")
    return render(Request,"forget-password-1.html")

def forgetPassword2(Request):
    username = Request.session.get("reset-password-user")
    if(Request.method=="POST"):
        otp = int(Request.POST.get("otp"))
        buyer = Buyer.objects.get(username=username)
        if(otp==buyer.otp):
            return HttpResponseRedirect("/forget-password-3/")
        else:
            error(Request,"Invalid OTP")
    if(username):
        return render(Request,"forget-password-2.html")
    else:
       return HttpResponseRedirect("/forget-password-1/") 

def forgetPassword3(Request):
    username = Request.session.get("reset-password-user")
    if(Request.method=="POST"):
        password = Request.POST.get("password")
        cpassword = Request.POST.get("cpassword")
        if(password==cpassword):
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            del Request.session['reset-password-user']
            return HttpResponseRedirect("/login/")
        else:
            error(Request,"Password and Confirm Password Doesn't Matched")
    if(username):
        return render(Request,"forget-password-3.html")
    else:
       return HttpResponseRedirect("/forget-password-1/") 




def signup(request):
    if(request.method=="POST"):
       password= request.POST.get("password")
       cpassword= request.POST.get("cpassword")
       if(password==cpassword):
        username= request.POST.get("username")
        email= request.POST.get("email")
        name= request.POST.get("name")
        try:
            User.objects.create_user(username=username,email=email,password=password,first_name=name)
            phone= request.POST.get("phone")

            b= Buyer()
            b.name= name
            b.username= username
            b.email= email
            b.phone= phone
            b.save()
            return HttpResponseRedirect("/login/")
        except:
           error(request," Username Already Taken")
       else:
          error(request,"Password and Conform Password Don't Match!!!!")
       
    return render(request,"signup.html")

@login_required(login_url="/login/")
def logoutPage(request):
   logout(request)
   return HttpResponseRedirect("/login/")


@login_required(login_url="/login/")
def profile(request):
   if(request.user.is_superuser):
      return HttpResponseRedirect("/admin/")
   buyer= Buyer.objects.get(username=request.user.username)
   wishlist= Wishlist.objects.filter(buyer=buyer)
   checkout= Checkout.objects.filter(buyer=buyer)
   orders=[]
   for item in checkout:
       cp=CheckoutProduct.objects.filter(checkout=item)
       orders.append({"checkout":item,"cp":cp})
   return render(request,"profile.html",{"buyer":buyer, 'wishlist':wishlist,"orders":orders})


@login_required(login_url="/login/")
def updateProfile(request):
    if request.user.is_superuser:
        return HttpResponseRedirect("/admin/")
    buyer = Buyer.objects.get(username=request.user.username)
    if request.method == "POST":
        buyer.name = request.POST.get("name")
        buyer.email = request.POST.get("email")
        buyer.phone = request.POST.get("phone")
        buyer.address = request.POST.get("address")
        buyer.pin = request.POST.get("pin")
        buyer.city = request.POST.get("city")
        buyer.state = request.POST.get("state")
        if request.FILES.get("pic"):
            buyer.pic = request.FILES.get("pic")
        buyer.save()
        return HttpResponseRedirect("/profile/")
        
    return render(request, "updateprofile.html", {"buyer": buyer})


@login_required(login_url="/login/")   
def addToWishlistPage(request,id):  
    buyer= Buyer.objects.get(username=request.user.username)
    product= Product.objects.get(id=id)
    try:
        w= Wishlist.objects.get(product=product,buyer=buyer)
    except:
        w=Wishlist()
        w.product = product
        w.buyer = buyer
        w.save()
    return HttpResponseRedirect("/profile")
 
 
    
@login_required(login_url="/login/")   
def deleteWishlist(request,id):
   try:
      w=Wishlist.objects.get(id=id)
      w.delete()
   except:
      pass
   return HttpResponseRedirect("/profile/")



client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY,settings.RAZORPAY_API_SECRET_KEY))
@login_required(login_url="/login/")
def checkout(Request):
    try:
        buyer = Buyer.objects.get(username=Request.user.username)
        cart = Request.session.get('cart',None)
        subtotal = 0
        shipping = 0
        total = 0
        if(cart):
            for value in cart.values():
                subtotal = subtotal + value['total']
            if(subtotal>0 and subtotal<1000):
                shipping = 150
            total = subtotal+shipping

        if(Request.method=="POST"):
            mode = Request.POST.get("mode")
            checkout = Checkout()
            checkout.buyer = buyer
            checkout.subtotal = subtotal
            checkout.total = total
            checkout.shipping = shipping
            checkout.save()

            for key,value in cart.items():
                p = Product.objects.get(id=int(key))
                cp = CheckoutProduct()
                
                cp.checkout = checkout
                cp.product = p
                cp.qty = value['qty']
                cp.total = value['total']
                cp.save()
                Request.session['cart']={}

            if(mode=="COD"):
                return HttpResponseRedirect('/confirmation/'+str(checkout.id)+"/")
            else:
                orderAmount = checkout.total*100
                orderCurrency = "INR"
                paymentOrder = client.order.create(dict(amount=orderAmount,currency=orderCurrency,payment_capture=1))
                paymentId = paymentOrder['id']
                checkout.paymentmode=1
                checkout.save()
                return render(Request,"pay.html",{
                    "amount":orderAmount,
                    "displayAmount":checkout.total,
                    "api_key":settings.RAZORPAY_API_KEY,
                    "order_id":paymentId,
                    "User":buyer,
                    "id":checkout.id
                })
        return render(Request,"checkout.html",{'buyer':buyer,'total':total,'shipping':shipping,'subtotal':subtotal,'cart':cart})
    except:
        return HttpResponseRedirect("/admin/")

    

@login_required(login_url="/login/")
def confirmation(request):
    try:
        buyer = Buyer.objects.get(username=request.user.username)
        checkout= Checkout.objects.filter(buyer=buyer).order_by("-id").first()
        cart = CheckoutProduct.objects.filter(checkout=checkout)
        subtotal = 0
        shipping = 0
        total = 0
        
        for item in cart:
            subtotal = subtotal + item.total
        if(subtotal>0 and subtotal<1000):
            shipping = 150
        total = subtotal+shipping
        
        return render(request,"confirmation.html",{'cart':cart,'subtotal':subtotal,'shipping':shipping,'total':total,'buyer':buyer,"checkout":checkout})
    except:
       return HttpResponseRedirect("/admin/")


def newslatterSubscribePage(Request):
    if(Request.method=="POST"):
        email = Request.POST.get("email")
        n = Newslatter()
        n.email = email
        try:
            n.save()
            success(Request,"Thanks to Subscibe Our Newslatter Service!!!")
        except:
            error(Request,"Your Email Id is Already Subscribed!!!")
        return HttpResponseRedirect("/")
    else:
        return HttpResponseRedirect("/")


def search(Request):
    if(Request.method=="POST"):
        search = Request.POST.get("search")
        try:
            maincategory = Maincategory.objects.get(name=search)
        except:
            maincategory = None
        try:
            subcategory = Subcategory.objects.get(name=search)
        except:
            subcategory = None
        try:
            brand = Brand.objects.get(name=search)
        except:
            brand = None

        products = Product.objects.filter(Q(name__icontains=search)|Q(maincategory=maincategory)|Q(subcategory=subcategory)|Q(brand=brand)|Q(color=search)|Q(description__icontains=search))
        maincategory = Maincategory.objects.all().order_by("-id")
        subcategory = Subcategory.objects.all().order_by("-id")
        brand = Brand.objects.all().order_by("-id")
        return render(Request,"shop.html",{'products':products,'maincategory':maincategory,'subcategory':subcategory,'brand':brand,'mc':"All",'sc':"All",'br':"All"})        
    else:
        return HttpResponseRedirect("/")
    

@login_required(login_url='/login/')
def paymentSuccess(request,id,rppid,rpoid,rpsid):
    check = Checkout.objects.get(id=id)
    check.rppid=rppid
    check.paymentstatus=1
    check.save()
    return HttpResponseRedirect('/confirmation/'+str(id)+"/")

@login_required(login_url='/login/')
def rePayment(Request,id):
    try:
        checkout = Checkout.objects.get(id=id)
        buyer = Buyer.objects.get(username=Request.user.username)
        orderAmount = checkout.total*100
        orderCurrency = "INR"
        paymentOrder = client.order.create(dict(amount=orderAmount,currency=orderCurrency,payment_capture=1))
        paymentId = paymentOrder['id']
        checkout.paymentmode=1
        checkout.save()
        return render(Request,"pay.html",{
            "amount":orderAmount,
            "displayAmount":checkout.total,
            "api_key":settings.RAZORPAY_API_KEY,
            "order_id":paymentId,
            "User":buyer,
            "id":id
        })
    except:
        return HttpResponseRedirect("/profile/")

