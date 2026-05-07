from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Blog main pages
    path('', views.blog_home, name='home'),
    path('posts/', views.blog_list, name='list'),
    path('create/', views.create_post, name='create'),
    path('my-posts/', views.my_posts, name='my_posts'),
    
    # Post management
    path('post/<int:pk>/', views.blog_detail, name='detail'),
    path('post/<int:pk>/edit/', views.edit_post, name='edit'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:pk>/like/', views.toggle_like, name='toggle_like'),

    # Filtering
    path('category/<int:pk>/', views.category_posts, name='category'),
]