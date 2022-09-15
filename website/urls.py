from django.urls import path

from . import views
from .loaded_data import params
urlpatterns = [
	path('', views.index,name="index"),
	path('main.css', views.maincss),
	path('<str:name>', views.make_static_files(params))
]