from django.urls import path
from .import views

urlpatterns = [
    path('make_post/', views.make_post, name='make_post'),
    path('follow/<int:pk>/', views.follow, name="follow"),
    path('unfollow/<int:pk>/', views.unfollow, name="unfollow"),
    path('edit_profile/', views.edit_profile, name="edit_profile"),
    path('search/', views.search, name='search'),
    path('like_post/<int:pk>', views.like_post, name='like_post'),
    path('unlike_post/<int:pk>', views.unlike_post, name='unlike_post'),
    path('comment/<int:post_id>', views.comment, name='comment'),
    path('post_details/<int:post_id>', views.post_details, name='post_details'),
    path('thinking', views.thinking, name='thinking'),
    path('delete_notification/<int:notification_id>/<int:post_id>', views.delete_notification, name='delete_notification'),
]