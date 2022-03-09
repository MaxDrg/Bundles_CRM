from django.urls import path
from . import views

urlpatterns = [
    path("folders", views.folders, name='folders'),
    path("devs", views.devs, name='devs'),
    path("form_devs", views.form_devs, name='form_devs'),
    path("apps", views.apps, name='apps'),
    path("app_info", views.app_info, name='app_info'),
    path("apps_dashboard", views.apps_dashboard, name='apps_dashboard'),
    path("admobs", views.admobs, name='admobs'),
    path("form_admob", views.form_admob, name='form_admob'),
    path("check_admob", views.check_admob, name='check_admob'),
    path("admob_info", views.admob_info, name='admob_info'),
]

# print(hashlib.sha256('dashboard'.encode('utf8')).hexdigest())