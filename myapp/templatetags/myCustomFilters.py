from django import template

register= template.Library()

@register.filter(name="paymentMode")
def paymentMode(request,num):
    if(num==0):
        return "COD"
    else:
        return "NetBanking"
   
@register.filter(name="paymentStatus")
def paymentStatus(request,num):
    if(num==0):
        return "Pending"
    else:
        return "Done"


@register.filter(name="orderStatus")
def orderStatus(request,num):
    if(num==0):
        return "Order is placed"
    elif(num==1):
        return "Order is packed"
    elif(num==2):
        return "Ready to Dispatch"
    elif(num==3):
        return "Dispatch"
    elif(num==4):
        return "Out for Delivery"
    else:
        return "Delivered"  
    

@register.filter(name="paymentCondition")
def paymentCondition(mode, status):
    if(mode==1 and status==0):
        return True
    else:
        return False