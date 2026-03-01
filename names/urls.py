from django.urls import path
from . import views

app_name = 'names'  

urlpatterns = [
    path('', views.home, name='home'),   
    path('analyze/', views.analyze_names, name='analyze_names'),       
]
