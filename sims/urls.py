from django.urls import path

from . import views
from .api.simulation_results import simuation_results, get_availible_data_index, get_availible_results_index, simuation_result_varying
urlpatterns = [
	path('graphs/', views.index,name="index"),
	path('graphs/ie', views.ie,name="importexport"),
	path('graphs/ie2', views.importexportView, name="importexport2"),
	path("api/ie", views.importexportAPI, name="importexportAPI"),
	path("api/results/index", get_availible_data_index),
	path("api/results/index_result", get_availible_results_index),
	path("api/results/data", simuation_results),
	path("api/results/vdata", simuation_result_varying),
	path("api/results/agglomerated_result", views.get_agglomerated_results),

]