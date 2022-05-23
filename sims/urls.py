from django.urls import path

from . import views

urlpatterns = [
	path('graphs/', views.index,name="index"),
	path('graphs/ie', views.ie,name="importexport"),
	path('graphs/ie2', views.importexportView, name="importexport2"),
	path("api/ie", views.importexportAPI, name="importexportAPI")
]