from django.urls import path
from .views import *

urlpatterns = [
    path('', technics, name='technics'),
    path('<int:pk>/', technics, name='technics'),
    path('ajax/load-departments/', ajax_load_departments, name='ajax_load_departments'),
    path('ajax/load-positions/', ajax_load_positions, name='ajax_load_positions'),
    path('organization/<int:pk>/', organization, name='organization'),
]
