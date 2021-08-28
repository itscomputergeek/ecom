from django.urls import path
from . import views


urlpatterns = [
    path("", views.index, name="ShopHome"),
    path("about/", views.about, name="AboutUs"),
    path("contact/", views.contact, name="ContactUs"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("search/", views.search, name="Search"),
    path("products/<int:id>", views.productView, name="ProductView"),
    path("checkout/", views.checkout, name="Checkout"),
    path("cod/", views.cod, name="Cod"),
    path("handlerequest/", views.handlerequest, name="HandleRequest"),
    path("signup/", views.handleSignup, name="HandleSignup"),
    path("login/", views.handleLogin, name="HandleLogin"),
    path("logout/", views.handleLogout, name="HandleLogout"),
    path("contact/login/", views.handleLogin, name="HandleLogin"),
    path("about/login/", views.handleLogin, name="HandleLogin"),
    path("checkout/login/", views.handleLogin, name="HandleLogin"),

]
