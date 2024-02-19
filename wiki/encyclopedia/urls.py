from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('<str:title>', views.entry_page, name='entry_page'),
    path('search/', views.search, name='search_results'),
    path('new_page/', views.create_new_page, name='new_page'),
    path('edit/<str:title>/', views.edit_entry, name='edit_entry'),
    path('random/', views.random_page, name='random_page'),
]

