from django.urls import path

from . import views

app_name = 'women'

urlpatterns = [
    path('', views.women_home, name='home'),
    path('about/', views.women_about, name='about'),
    path('mission-vision/', views.women_mission_vision, name='mission_vision'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
    path('courses/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('progress/<int:lesson_id>/complete/', views.mark_lesson_complete, name='mark_lesson_complete'),
    path('my-learning/', views.my_learning, name='my_learning'),
]
