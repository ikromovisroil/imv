from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('organization/<int:pk>', organization, name='organization'),
    path('technics/<int:pk>', technics, name='technics'),
    path('technics_all/', technics_all, name='technics_all'),
    path('ajax/load-departments/', ajax_load_departments, name='ajax_load_departments'),
    path('ajax/load-positions/', ajax_load_positions, name='ajax_load_positions'),
]
