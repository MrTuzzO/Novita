from django.urls import path

from . import views

app_name = 'babycare'

urlpatterns = [
    path('request/', views.request_care, name='request_care'),
    path('track-status/', views.track_status, name='track_status'),
    path('requests/<str:request_id>/', views.request_detail, name='request_detail'),
    path('my-requests/', views.my_requests, name='my_requests'),
]
