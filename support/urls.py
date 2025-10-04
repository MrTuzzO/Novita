from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    # User views
    path('', views.ticket_list, name='dashboard'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('create/', views.create_ticket, name='create_ticket'),
    path('ticket/<str:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/<str:ticket_id>/close/', views.close_ticket, name='close_ticket'),
    path('attachment/<int:attachment_id>/download/', views.download_attachment, name='download_attachment'),
]