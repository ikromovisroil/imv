from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('technics/', technics, name='technics'),
    path('technics/<int:pk>/', technics, name='technics'),
    path('ajax/load-departments/', ajax_load_departments, name='ajax_load_departments'),
    path('ajax/load-positions/', ajax_load_positions, name='ajax_load_positions'),
    path('organization/<int:pk>/', organization, name='organization'),
    path('document/', document_get, name='document_get'),
    path('document/document_post/', document_post, name='document_post'),
    path('technics_count/', get_technics_count, name='get_technics_count'),
    path('hisobot/', hisobot_get, name='hisobot_get'),
    path('hisobot/hisobot_post/', hisobot_post, name='hisobot_post'),

]
