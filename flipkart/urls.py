from django.contrib import admin
from django.urls import path
from myapp import views as myapp
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("",myapp.index,name="index"),
    path("about/",myapp.about,name="about"),
    path("add-to-card/",myapp.addToCart,name="add-to-card"),
    path("cart/",myapp.cart,name="cart"),
    path('delete-cart/<str:id>/', myapp.deleteCart,name="delete-cart"),
    path('update-cart/<str:id>/<str:op>/', myapp.updateCart,name="update-cart"),
    path("checkout/",myapp.checkout,name="checkout"),
    path('payment-success/<int:id>/<str:rppid>/<str:rpoid>/<str:rpsid>/', myapp.paymentSuccess,name="payment-success"),
    path('re-payment/<int:id>/', myapp.rePayment,name="re-payment"),

    path("confirmation/",myapp.confirmation,name="confirmation"),
    path("contact/",myapp.contact,name="contact"),
    path("login/",myapp.login,name="login"),
    path("logout/",myapp.logoutPage,name="logout"),

    path("signup/",myapp.signup,name="signup"),
    path("profile/",myapp.profile,name="profile"),
    path("updateprofile/",myapp.updateProfile,name="updateprofile"),

    path("shop/<str:mc>/<str:sc>/<str:br>/",myapp.shop,name="shop"),
    path("singleproduct/<int:id>/",myapp.singleproduct,name="singleproduct"),
    path("add-to-wishlist/<int:id>/",myapp.addToWishlistPage,name="add-to-wishlist"),
    path("delete-wishlist/<int:id>/",myapp.deleteWishlist,name="delete-wishlist"),
    path('newslatter/subscribe/',myapp.newslatterSubscribePage,name="newsletter-subscribe"),
    path('search/',myapp.search,name="search"),

    path('forget-password-1/',myapp.forgetPassword1,name="forget-password-1"),
    path('forget-password-2/',myapp.forgetPassword2,name="forget-password-2"),
    path('forget-password-3/',myapp.forgetPassword3,name="forget-password-3"),

]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

