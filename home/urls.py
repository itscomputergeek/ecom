from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("signup/", views.handleSignup, name="HandleSignup"),
    path("login/", views.handleLogin, name="HandleLogin"),
    path("logout/", views.handleLogout, name="HandleLogout"),
   ]