from sims.utils import get_bool_param, get_float_param, get_int_param, get_date_param, printw, get_raw_param, get_int_array_param
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from . import simulated_data, sim_prop_index, sim_result_index
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
	return_index = get_int_param(request, "return_index", sim_result_index.autosuffisiency.value)
	first_min    = get_float_param(request, "first_min" , get_boundaries(simulated_data, first_index) [0])
	first_max    = get_float_param(request, "first_max" , get_boundaries(simulated_data, first_index) [1])
	second_min   = get_float_param(request, "second_min", get_boundaries(simulated_data, second_index)[0])
	second_max   = get_float_param(request, "second_max", get_boundaries(simulated_data, second_index)[1])

	indexes = [index.value for index in sim_prop_index]
	indexes.remove(first_index)
	indexes.remove(second_index)
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
				if not first in toReturnData:
					toReturnData[first] = {}
				toReturnData[first][second] = data
				
	response = HttpResponse(json.dumps(toReturnData))
	response["Content-Type"] = "application/JSON"
	return response

@csrf_exempt
def get_availible_data_index(request : HttpRequest) -> HttpResponse:
	responseData = json.dumps({
		"wind_production"      : {
			"index"           :  sim_prop_index.wind.value,
			"possible_values" : get_possible_values(simulated_data, sim_prop_index.wind.value)
		},
		"solar_production"     : {
			"index"           :  sim_prop_index.sun.value,
			"possible_values" : get_possible_values(simulated_data, sim_prop_index.sun.value)
		},
		"bioenergy_production" : {
			"index"           :  sim_prop_index.bio.value,
			"possible_values" : get_possible_values(simulated_data, sim_prop_index.bio.value)
		},
		"battery_capacity"     : {
			"index"           :  sim_prop_index.battery.value,
			"possible_values" : get_possible_values(simulated_data, sim_prop_index.battery.value)
		},
		"flexibility"          : {
			"index"           :  sim_prop_index.flexibility.value,
			"possible_values" : get_possible_values(simulated_data, sim_prop_index.flexibility.value)
		},
	})
	response = HttpResponse(responseData)
	response["Content-Type"] = "application/JSON"
	return response