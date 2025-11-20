from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('deed/seen/', deed_mark_seen, name="deed_mark_seen"),
    path("deed/<int:pk>/action/", deed_action, name="deed_action"),
    path('contact/', contact, name='contact'),
    path("get_employee_files/", get_employee_files, name="get_employee_files"),
    path('deed_post/', deed_post, name='deed_post'),
    path('technics/', technics, name='technics'),
    path('technics/<slug:slug>/', technics, name='technics'),
    path('ajax/load-departments/', ajax_load_departments, name='ajax_load_departments'),
    path('ajax/load-directorate/', ajax_load_directorate, name='ajax_load_directorate'),
    path('ajax/load-division/', ajax_load_division, name='ajax_load_division'),
    path('organization/<slug:slug>/', organization, name='organization'),
    path('document/', document_get, name='document_get'),
    path('document/document_post/', document_post, name='document_post'),
    path('document/technics_count/', get_technics_count, name='get_technics_count'),
    path('hisobot/', hisobot_get, name='hisobot_get'),
    path('hisobot/hisobot_post/', hisobot_post, name='hisobot_post'),
    path('hisobot/ajax/technics/', ajax_load_technics, name='ajax_load_technics'),
]
