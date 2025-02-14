from django.urls import path
from . import views

urlpatterns = [
    path('', views.display_data, name='display_data'),
    path('add/', views.add_data, name='add_data'),
    path('delete/<int:product_id>/', views.delete_product, name='delete_product'),

]