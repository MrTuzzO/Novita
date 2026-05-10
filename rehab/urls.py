from django.urls import path

from . import views

app_name = 'rehab'

urlpatterns = [
    path('admission/request/', views.request_admission, name='request_admission'),
    path('track-status/', views.track_status, name='track_status'),
    path('applications/<str:application_id>/', views.application_detail, name='application_detail'),
    path('my-applications/', views.my_applications, name='my_applications'),
]
