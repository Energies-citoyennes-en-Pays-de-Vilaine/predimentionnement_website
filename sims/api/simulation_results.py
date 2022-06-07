from sims.utils import get_bool_param, get_float_param, get_int_param, get_date_param, printw, get_raw_param, get_int_array_param
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from . import simulated_data, sim_prop_index, sim_result_index
from sims.modules.predim.configuration import config
from typing import *
import json

def get_boundaries(data : List[List[float]], index : int) -> Tuple[float, float]:
	mini = data[0][index]
	maxi = data[0][index]
	for d in data:
		if d[index] < mini:
			mini = d[index]
		if d[index] > maxi:
			maxi = d[index]
	return (mini, maxi)
def get_possible_values(data: List[List[float]], index : int) -> List[float]:
	toReturn = set()
	for d in data:
		toReturn.add(d[index])
	return sorted(list(toReturn))

@csrf_exempt
def simuation_results(request : HttpRequest) -> HttpResponse:
	first_index  = get_int_param(request, "first_index", sim_prop_index.wind.value)
	second_index = get_int_param(request, "second_index", sim_prop_index.sun.value)
	return_index = get_int_param(request, "return_index", sim_result_index.export_avg.value)
	first_min    = get_float_param(request, "first_min" , get_boundaries(simulated_data, first_index) [0])
	first_max    = get_float_param(request, "first_max" , get_boundaries(simulated_data, first_index) [1])
	second_min   = get_float_param(request, "second_min", get_boundaries(simulated_data, second_index)[0])
	second_max   = get_float_param(request, "second_max", get_boundaries(simulated_data, second_index)[1])
	first_scale  = get_float_param(request, "first_scale", 1.0)
	second_scale  = get_float_param(request, "second_scale", 1.0)
	result_scale  = get_float_param(request, "result_scale", 1.0)
	indexes = [index.value for index in sim_prop_index]
	try:
		indexes.remove(first_index)
		indexes.remove(second_index)
	except ValueError:
		printw(first_index, "i ", second_index)
	fixed_indexes = get_int_array_param(request, "fixed_indexes", indexes)# this is needed to get the order of the fixed params
	fixed_indexes = list(set(fixed_indexes))
	for i in fixed_indexes:
		try:
			indexes.remove(i)
		except ValueError:
			printw(f"{i} is not in the list {indexes} could not remove it")
	fixed_indexes = fixed_indexes + indexes
	fixed_values = [get_boundaries(simulated_data, i)[0] for i in fixed_indexes]	
	fixed_values = get_float_param(request, "fixed_values", fixed_values)

	toReturnData = {}
	for d in simulated_data:
		first  = d[first_index]
		second = d[second_index]
		data   = d[return_index]
		if (first >= first_min and first <= first_max):
			if (second >= second_min and second <= second_max):
				toAdd = True
				for i in range(len(fixed_indexes)):
					if d[fixed_indexes[i]] != fixed_values[i]:
						toAdd = False
				if (toAdd != True):
					continue
				first *= first_scale
				second *= second_scale
				data *= result_scale
				if not first in toReturnData:
					toReturnData[first] = {}
				toReturnData[first][second] = data
	non_sorted_to_return_data = toReturnData.copy()
	toReturnData = {}
	for key in sorted(non_sorted_to_return_data.keys()):
		
		toReturnData[key] = {}
		for ykey in sorted(non_sorted_to_return_data[key].keys()):
			toReturnData[key][ykey] = non_sorted_to_return_data[key][ykey]
	response = HttpResponse(json.dumps(toReturnData))
	response["Content-Type"] = "application/JSON"
	return response

@csrf_exempt
def get_availible_data_index(request : HttpRequest) -> HttpResponse:
	responseData = json.dumps({
		"wind_production"      : {
			"index"           : sim_prop_index.wind.value,
			"name"            : "production éolienne(MWh/an)",
			"short_name"      : "Eolien(MWh/an)",
			"suggested_scale" : 365 * 24 * (config.CA_PONTCHATEAU_POPULATION + config.CA_REDON_POPULATION) / 1000000,
			"possible_values" : get_possible_values(simulated_data, sim_prop_index.wind.value)
		},
		"solar_production"     : {
			"index"           :  sim_prop_index.sun.value,
			"name"            : "production photovoltaique(MWh/an)",
			"short_name"      : "Solaire(MWh/an)",
			"suggested_scale" : 365 * 24 * (config.CA_PONTCHATEAU_POPULATION + config.CA_REDON_POPULATION) / 1000000,
			"possible_values" : get_possible_values(simulated_data, sim_prop_index.sun.value)
		},
		"bioenergy_production" : {
			"index"           :  sim_prop_index.bio.value,
			"name"            : "production de bioenergie(MWh/an)",
			"short_name"      : "Bioenergie(MWh/an)",
			"suggested_scale" : 365 * 24 * (config.CA_PONTCHATEAU_POPULATION + config.CA_REDON_POPULATION) / 1000000,
			"possible_values" : get_possible_values(simulated_data, sim_prop_index.bio.value)
		},
		"battery_capacity"     : {
			"index"           :  sim_prop_index.battery.value,
			"name"            : "capacité de stockage (MWh)",
			"short_name"      : "Stockage(MWh)",
			"suggested_scale" : 1.0,
			"possible_values" : get_possible_values(simulated_data, sim_prop_index.battery.value)
		},
		"flexibility"          : {
			"index"           :  sim_prop_index.flexibility.value,
			"name"            : "taux de flexibilité",
			"short_name"      : "Flexibilite(ratio)",
			"suggested_scale" : 1.0,
			"possible_values" : get_possible_values(simulated_data, sim_prop_index.flexibility.value)
		},
	})
	response = HttpResponse(responseData)
	response["Content-Type"] = "application/JSON"
	return response