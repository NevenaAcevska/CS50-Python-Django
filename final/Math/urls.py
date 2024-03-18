from django.urls import path

from Math import views

urlpatterns = [

    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('start-game/', views.generate_question, name='start_game'),
    path('generate-question/', views.generate_question, name='generate_question'),
    path('check-answer/', views.check_answer, name='check_answer'),
    path('scoreboard/', views.scoreboard, name='scoreboard')
]
    #path('create/', views.create_listing, name='create_listing'),
    #path('listing/<int:listing_id>/', views.listing_page, name='listing_page'),
    #path('watchlist/', views.watchlist, name='watchlist'),
    #path('categories/', views.categories, name='categories'),
    #path('category/<str:category>/', views.category_listings, name='category_listings')

