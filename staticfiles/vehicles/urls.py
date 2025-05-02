
from django.urls import path

from . import views

urlpatterns = [
    path('', views.vehicles, name='vehicles'),
    path('vehicle_list/', views.vehicle_list, name='vehicle_list'),
    path('vehicle/<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle_detail'),
    path('vehicle_form/', views.VehicleCreateView.as_view(), name='vehicle_form'),
    path('vehicle_update/<int:pk>/', views.VehicleUpdateView.as_view(), name='vehicle_update'),
    path('vehicle_delete/<int:pk>/', views.VehicleDeleteView.as_view(), name='vehicle_delete'),
    path('vehicle_list_text', views.vehicle_list_txt, name='vehicle_list_text'),
    path('vehicle_list_csv', views.vehicle_list_csv, name='vehicle_list_csv'),
    path('vehicle_search/', views.VehicleSearchView.as_view(), name='vehicle_search'),
    path('vehicle_detail_txt/<int:pk>/', views.vehicle_detail_txt, name='vehicle_detail_txt'),
    path('vehicle_detail_pdf/<int:pk>/', views.vehicle_detail_pdf, name='vehicle_detail_pdf'),
    path('vehicle_detail_pdf/<int:pk>/', views.vehicle_detail_pdf, name='vehicle_detail_pdf'),
    ]
