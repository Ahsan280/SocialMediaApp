from django.urls import path
from .import views

urlpatterns = [
    path("", views.index, name="index"),
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>', views.activate, name="activate"),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('user_details/<int:pk>/', views.user_details, name="user_details"),

]