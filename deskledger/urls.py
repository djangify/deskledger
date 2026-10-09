from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

# import your new home & dashboard views
from .views import (
    home,
    dashboard,
    logout_view,
    switch_tax_year,
    health_check,
    protected_media,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", health_check, name="health_check"),
    # Receipts: login required + owner check (see views.protected_media)
    path("media/<path:path>", protected_media, name="protected_media"),
    path("accounts/", include("allauth.urls")),
    # Auth
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="auth/login.html"),
        name="login",
    ),
    # use custom logout
    path("logout/", logout_view, name="logout"),
    # NEW Home + Dashboard
    path("", home, name="home"),
    path("dashboard/", dashboard, name="dashboard"),
    path("switch-year/<str:tax_year>/", switch_tax_year, name="switch_tax_year"),
    # Apps
    path("accounts/", include("accounts.urls", namespace="accounts")),
    path("business/", include("business.urls", namespace="business")),
    path("bookkeeping/", include("bookkeeping.urls", namespace="bookkeeping")),
]
# Adminita - Admin customization
admin.site.site_header = "Bookkeeping Software"
admin.site.site_title = "Bookkeeping Software"
admin.site.index_title = "Welcome to Your Site"
