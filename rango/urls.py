from django.urls import path
from rango import views

app_name = 'rango'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('category/<slug:category_name_slug>/add_page/', views.add_page,
            name='add_page'),
    path('category/<slug:category_name_slug>/', views.show_category,
            name='show_category'),
    path('add_category/', views.add_category, 
            name='add_category'), 
    #path('register/', views.register, name='register'),
    #path('login/', views.user_login, name='login'),
    #path('logout/', views.user_logout, name='logout'),
    path('restricted/', views.restricted, name='restricted'),
    path('search/', views.search, name='search'),
    path('rango/goto/', views.goto_url, name='goto'),
    path('profile/<username>/', views.ProfileView.as_view(), name='profile'),
    path('profiles/', views.ListProfilesView.as_view(), name='list_profiles'),
    #path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('register_profile/', views.register_profile, name='register_profile'),
    path('accounts/register/', views.MyRegistrationView.as_view(), name='registration_register'),
    path('like_category/', views.LikeCategoryView.as_view(), name='like_category'),
    path('suggest/', views.CategorySuggestionView.as_view(), name='suggest'),
]