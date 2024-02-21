from django.urls import path

from . import views
from .views import create_listing, active_listings, listing_page, watchlist, categories, category_listings

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('create/', create_listing, name='create_listing'),
    path('', active_listings, name='active_listings'),
    path('listing/<int:listing_id>/', listing_page, name='listing_page'),
    path('watchlist/', watchlist, name='watchlist'),
    path('categories/', categories, name='categories'),
    path('category/<str:category>/', category_listings, name='category_listings')
]
