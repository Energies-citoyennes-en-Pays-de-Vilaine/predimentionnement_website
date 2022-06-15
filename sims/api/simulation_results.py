from sims.utils import get_bool_param, get_float_param, get_int_param, get_date_param, printw, get_raw_param, get_int_array_param, get_float_array_param
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from . import sim_prop_index, sim_result_index, sorted_simulated_data, sim_result_indexes_list
from sims.modules.predim.configuration import config
from typing import *
import json
import os
from ctypes import *
import numpy as np
from time import time
libfilter = CDLL(os.path.dirname(os.path.realpath(__file__)) + "/../modules/cmodules/libfilter/libfilter.so")
GREATER_THAN = 1
GREATER_EQUAL = 2
SMALLER_THAN = 3
SMALLER_EQUAL = 4
EQUAL = 5
#TODO make a python module wrapper for libfilter
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

def get_index(sim_result_indexes_list : List[List[float]], values : List[float]) -> int:
	index = 0
	for i in range(len(values)):
		index *= len(sim_result_indexes_list[i])
		index += sim_result_indexes_list[i].index(values[i])
	return index

@csrf_exempt
def simuation_results(request : HttpRequest) -> HttpResponse:
	t0 = time()
	first_index  = get_int_param(request, "first_index", sim_prop_index.wind.value)
	second_index = get_int_param(request, "second_index", sim_prop_index.sun.value)
	return_index = get_int_param(request, "result_index", sim_result_index.export_avg.value)
	first_min    = get_float_param(request, "first_min" , sim_result_indexes_list[first_index][0])
	first_max    = get_float_param(request, "first_max" , sim_result_indexes_list[first_index][-1])
	second_min    = get_float_param(request, "second_min" , sim_result_indexes_list[second_index][0])
	second_max    = get_float_param(request, "second_max" , sim_result_indexes_list[second_index][-1])
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
	fixed_values = [sim_result_indexes_list[i][0] for i in fixed_indexes]
	fixed_values = get_float_array_param(request, "fixed_values", fixed_values)
	indexes_to_use = [0 for i in range(len(sim_result_indexes_list))]
	toReturnData = {}
	toReturnData = {}
	for first in sim_result_indexes_list[first_index]:
		if (first < first_min or first > first_max):
			continue
		toReturnData[first * first_scale] = {}
		for second in sim_result_indexes_list[second_index]:
			if (second < second_min or second > second_max):
				continue
			indexes_to_use[first_index] = first
			indexes_to_use[second_index] = second
			for index in range(len(fixed_indexes)):
				indexes_to_use[fixed_indexes[index]] = fixed_values[index]
			toReturnData[first * first_scale][second * second_scale] = sorted_simulated_data[get_index(sim_result_indexes_list, indexes_to_use)][return_index] * result_scale
	
	response = HttpResponse(json.dumps(toReturnData))
	response["Content-Type"] = "application/JSON"
	print(time() - t0)
	return response


def get_variations(arrayToRetrun, current_choices, arrayOfChoices):
	if len(arrayOfChoices) == 0:
			arrayToRetrun.append(current_choices[:])
			return
	else:
		for choice in arrayOfChoices[0]:
			get_variations(arrayToRetrun, current_choices[:] + [choice], arrayOfChoices[1:])
	return arrayToRetrun

@csrf_exempt
def simuation_result_varying(request : HttpRequest) -> HttpResponse:
	t0 = time()
	varyin_indexes  = get_int_array_param(request, "varying_indexes",  [sim_prop_index.wind.value])
	varying_mins    = get_float_array_param(request, "varying_mins" , [sim_result_indexes_list[i][0] for i in varyin_indexes])
	varying_maxs    = get_float_array_param(request, "varying_maxs" , [sim_result_indexes_list[i][-1] for i in varyin_indexes])
	varying_scales  = get_float_array_param(request, "varying_scales", [1.0] * len(varyin_indexes))
	return_index    = get_int_param(request, "result_index", sim_result_index.export_avg.value)
	result_scale    = get_float_param(request, "result_scale", 1.0)

	indexes = [index.value for index in sim_prop_index]
	try:
		for i in varyin_indexes:
			indexes.remove(i)
	except ValueError:
		printw("indexes used multiple times", indexes)
	fixed_indexes = get_int_array_param(request, "fixed_indexes", indexes)# this is needed to get the order of the fixed params
	fixed_indexes = list(set(fixed_indexes))
	for i in fixed_indexes:
		try:
			indexes.remove(i)
		except ValueError:
			printw(f"{i} is not in the list {indexes} could not remove it")
	fixed_indexes = fixed_indexes + indexes
	fixed_values = [sim_result_indexes_list[i][0] for i in fixed_indexes]
	fixed_values = get_float_array_param(request, "fixed_values", fixed_values)
	indexes_to_use = [0 for i in range(len(sim_result_indexes_list))]
	toReturnData = {}
	toReturnData = {}
	permutations_to_check = []
	for i in varyin_indexes:
		permutations_to_check.append(sim_result_indexes_list[i])
	variations = []
	variations = get_variations(variations, [], permutations_to_check)
	result = {}
	current_result = result#TODO rename those
	last_result = current_result
	for variation in variations:
		is_valid_variation = True
		for i in range(len(variation)):
			if (variation[i] < varying_mins[i] or variation[i] > varying_maxs[i]):
				is_valid_variation = False
				break
			indexes_to_use[varyin_indexes[i]] = variation[i]
		if not is_valid_variation:
			continue
		for index in range(len(fixed_indexes)):
			indexes_to_use[fixed_indexes[index]] = fixed_values[index]
		current_result = result
		for i in range(len(variation)):
			try:
				current_result[variation[i] * varying_scales[i]]
			except KeyError:
				current_result[variation[i] * varying_scales[i]] = {}
			last_result = current_result
			current_result = current_result[variation[i] * varying_scales[i]]
		last_result[variation[i] * varying_scales[i]] = sorted_simulated_data[get_index(sim_result_indexes_list, indexes_to_use)][return_index] * result_scale
	response = HttpResponse(json.dumps(result))
	response["Content-Type"] = "application/JSON"
	return response


@csrf_exempt
def get_availible_data_index(request : HttpRequest) -> HttpResponse:
	responseData = json.dumps({
		"wind_production"      : {
			"index"           : sim_prop_index.wind.value,
			"name"            : "production éolienne(GWh/an)",
			"short_name"      : "Eolien(GWh/an)",
			"suggested_scale" : 365.0 * 24.0 * (config.CA_PONTCHATEAU_POPULATION + config.CA_REDON_POPULATION) / 1e9,
			"possible_values" : sim_result_indexes_list[sim_prop_index.wind.value]
		},
		"solar_production"     : {
			"index"           :  sim_prop_index.sun.value,
			"name"            : "production photovoltaique(GWh/an)",
			"short_name"      : "Solaire(GWh/an)",
			"suggested_scale" : 365.0 * 24.0 * (config.CA_PONTCHATEAU_POPULATION + config.CA_REDON_POPULATION) / 1e9,
			"possible_values" : sim_result_indexes_list[sim_prop_index.sun.value]
		},
		"bioenergy_production" : {
			"index"           :  sim_prop_index.bio.value,
			"name"            : "production de bioenergie(GWh/an)",
			"short_name"      : "Bioenergie(GWh/an)",
			"suggested_scale" : 365.0 * 24.0 * (config.CA_PONTCHATEAU_POPULATION + config.CA_REDON_POPULATION) / 1e9,
			"possible_values" : sim_result_indexes_list[sim_prop_index.bio.value]
		},
		"battery_capacity"     : {
			"index"           :  sim_prop_index.battery.value,
			"name"            : "capacité de stockage (MWh)",
			"short_name"      : "Stockage(MWh)",
			"suggested_scale" : (config.CA_REDON_POPULATION + config.CA_PONTCHATEAU_POPULATION) / 1e6,
			"possible_values" : sim_result_indexes_list[sim_prop_index.battery.value]
		},
		"flexibility"          : {
			"index"           :  sim_prop_index.flexibility.value,
			"name"            : "taux de flexibilité",
			"short_name"      : "Flexibilite(ratio)",
			"suggested_scale" : 100,
			"possible_values" : sim_result_indexes_list[sim_prop_index.flexibility.value]
		},
	})
	response = HttpResponse(responseData)
	response["Content-Type"] = "application/JSON"
	return response

@csrf_exempt
def get_availible_results_index(request : HttpRequest) -> HttpResponse:
	responseData = json.dumps({
		"storage_use"      : {
			"index"           : sim_result_index.storage_use.value,
			"name"            : "utilisation du stockage (pourcent de la capacité)",
			"short_name"      : "stockage",
			"suggested_scale" : 100,
		},
		"imported_power"   : {
			"index"           : sim_result_index.import_avg.value,
			"name"            : "puissance importée (GWh/an)",
			"short_name"      : "imports",
			"suggested_scale" : (config.CA_REDON_POPULATION + config.CA_PONTCHATEAU_POPULATION) * 365 * 24 / 1e9,
		},
		"exported_power"   :
		{
			"index"           : sim_result_index.export_avg.value,
			"name"            : "puissance exportée (GWh/an)",
			"short_name"      :	"exports",
			"suggested_scale" : (config.CA_REDON_POPULATION + config.CA_PONTCHATEAU_POPULATION) * 365 * 24 / 1e9,
		},
		"autoconso"        :
		{
			"index"           : sim_result_index.autoconso.value,
			"name"            : "autoconsommation (%)",
			"short_name"      : "autoconsommation",
			"suggested_scale" : 100,
		},
		"imported_time"    :
		{
			"index"           : sim_result_index.import_time.value,
			"name"            : "proportion du temps ou le territoire importe(%)",
			"short_name"      : "taux temporel d'import",
			"suggested_scale" : 100,
		},
		"exported_time"    :
		{
			"index"           : sim_result_index.export_time.value,
			"name"            : "proportion du temps ou le territoire exporte(%)",
			"short_name"      : "taux temporel d'export",
			"suggested_scale" : 100,
		},
		"low_conso_peak"   :
		{
			"index"           : sim_result_index.low_conso_peak.value,
			"name"            : "5%tile de consommation",
			"short_name"      : "5% consommation (GWh/an)",
			"suggested_scale" : (config.CA_REDON_POPULATION + config.CA_PONTCHATEAU_POPULATION) * 365 * 24 / 1e9,
		},
		"high_conso_peak"  :
		{
			"index"           : sim_result_index.high_conso_peak.value,
			"name"            : "95%tile de consommation",
			"short_name"      : "95% consommation (GWh/an)",
			"suggested_scale" : (config.CA_REDON_POPULATION + config.CA_PONTCHATEAU_POPULATION) * 365 * 24 / 1e9,
		},
		"low_import_peak"  :
		{
			"index"           : sim_result_index.low_import_peak.value,
			"name"            : "5%tile d'import (GWh/an)",
			"short_name"      : "5% import",
			"suggested_scale" : (config.CA_REDON_POPULATION + config.CA_PONTCHATEAU_POPULATION) * 365 * 24 / 1e9,
		},
		"high_import_peak" :
		{
			"index"           : sim_result_index.high_import_peak.value,
			"name"            : "95%tile d'import (GWh/an)",
			"short_name"      : "95% import",
			"suggested_scale" : (config.CA_REDON_POPULATION + config.CA_PONTCHATEAU_POPULATION) * 365 * 24 / 1e9,
		},
		"flexibility_use" :
		{
			"index"           : sim_result_index.felxibility_use.value,
			"name"            : "utilisation de la flexibilité (%)",
			"short_name"      : "flex moyenne",
			"suggested_scale" : 100,
		}
	})
	response = HttpResponse(responseData)
	response["Content-Type"] = "application/JSON"
	return response