from django.urls import path

from . import views

app_name = 'service'

urlpatterns = [
    path('', views.ServiceListView.as_view(), name='service_list'),
    path('contact/', views.create_inquiry, name='create_inquiry'),
    path('requests/', views.inquiry_list, name='inquiry_list'),
    path('expert/inbox/', views.expert_inbox, name='expert_inbox'),
    path('requests/<str:inquiry_id>/', views.inquiry_detail, name='inquiry_detail'),
    path('requests/<str:inquiry_id>/close/', views.close_inquiry, name='close_inquiry'),
    path('attachments/<int:attachment_id>/download/', views.download_attachment, name='download_attachment'),
    path('experts/<int:pk>/', views.expert_profile, name='expert_profile'),
    path('<slug:slug>/', views.service_detail, name='service_detail'),
]
