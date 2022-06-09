from sims.utils import get_bool_param, get_float_param, get_int_param, get_date_param, printw, get_raw_param, get_int_array_param, get_float_array_param
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from . import simulated_data, sim_prop_index, sim_result_index, simulated_data_np
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

@csrf_exempt
def simuation_results(request : HttpRequest) -> HttpResponse:
	first_index  = get_int_param(request, "first_index", sim_prop_index.wind.value)
	second_index = get_int_param(request, "second_index", sim_prop_index.sun.value)
	return_index = get_int_param(request, "result_index", sim_result_index.export_avg.value)
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
	fixed_values = get_float_array_param(request, "fixed_values", fixed_values)
	toReturnData = {}
	#this is the part that will be optimized as it's too slow
	t0 = time()
	criterions_values = np.array([first_min, first_max, second_min, second_max] + fixed_values, dtype=np.float64)
	criterions_types = np.array([GREATER_EQUAL, SMALLER_EQUAL, GREATER_EQUAL, SMALLER_EQUAL] + [EQUAL for i in range(len(fixed_values))], dtype=np.int64)
	criterions_positions = np.array([first_index, first_index, second_index, second_index] + fixed_indexes, dtype=np.int64)
	to_check = simulated_data_np
	output_count = c_int32()
	output_data = POINTER(c_double)()
	t0 = time()
	libfilter.get_filtered_data(
		to_check.ctypes.data_as(POINTER(c_double)),
		to_check.shape[0],
		to_check.shape[1],
		criterions_types.ctypes.data_as(POINTER(c_int64)),
		criterions_values.ctypes.data_as(POINTER(c_double)),
		criterions_positions.ctypes.data_as(POINTER(c_int64)),
		len(criterions_types),
		byref(output_data),
		byref(output_count))
	print("time00", time() - t0)
	toReturnData2 = {}
	result2_array = []
	result_array  = []
	for i in range(output_count.value):
		first = output_data[i * to_check.shape[1] + first_index]
		second = output_data[i * to_check.shape[1] + second_index]
		data   = output_data[i * to_check.shape[1] + return_index]
		first *= first_scale
		second *= second_scale
		data *= result_scale
		result2_array.append([first,second,data])
		if not first in toReturnData2:
			toReturnData2[first] = {}
		toReturnData2[first][second] = data

	libfilter.freeArray(output_data)
	print("time0 ",time() - t0)
	t0 = time()
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
				result_array.append([first,second,data])
				if not first in toReturnData:
					toReturnData[first] = {}
				toReturnData[first][second] = data
	non_sorted_to_return_data = toReturnData.copy()
	print("time1 ",time() - t0)
	toReturnData = {}
	for key in sorted(non_sorted_to_return_data.keys()):
		toReturnData[key] = {}
		for ykey in sorted(non_sorted_to_return_data[key].keys()):
			toReturnData[key][ykey] = non_sorted_to_return_data[key][ykey]
			if (toReturnData2[key][ykey] != toReturnData[key][ykey]):
				print(key,ykey, toReturnData2[key][ykey], toReturnData[key][ykey])
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
			"suggested_scale" : (config.CA_PONTCHATEAU_POPULATION + config.CA_REDON_POPULATION) / 1000000,
			"possible_values" : get_possible_values(simulated_data, sim_prop_index.battery.value)
		},
		"flexibility"          : {
			"index"           :  sim_prop_index.flexibility.value,
			"name"            : "taux de flexibilité",
			"short_name"      : "Flexibilite(ratio)",
			"suggested_scale" : 100,
			"possible_values" : get_possible_values(simulated_data, sim_prop_index.flexibility.value)
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
			"name"            : "puissance importée (MWh/an)",
			"short_name"      : "imports",
			"suggested_scale" : (config.CA_REDON_POPULATION + config.CA_PONTCHATEAU_POPULATION) * 365 * 24 / 1e6,
		},
		"exported_power"   :
		{
			"index"           : sim_result_index.export_avg.value,
			"name"            : "puissance exportée (MWh/an)",
			"short_name"      :	"exports",
			"suggested_scale" : (config.CA_REDON_POPULATION + config.CA_PONTCHATEAU_POPULATION) * 365 * 24 / 1e6,
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
			"short_name"      : "5% consommation",
			"suggested_scale" : (config.CA_REDON_POPULATION + config.CA_PONTCHATEAU_POPULATION) * 365 * 24 / 1e6,
		},
		"high_conso_peak"  :
		{
			"index"           : sim_result_index.high_conso_peak.value,
			"name"            : "95%tile de consommation",
			"short_name"      : "95% consommation",
			"suggested_scale" : (config.CA_REDON_POPULATION + config.CA_PONTCHATEAU_POPULATION) * 365 * 24 / 1e6,
		},
		"low_import_peak"  :
		{
			"index"           : sim_result_index.low_import_peak.value,
			"name"            : "5%tile d'import",
			"short_name"      : "5% import",
			"suggested_scale" : (config.CA_REDON_POPULATION + config.CA_PONTCHATEAU_POPULATION) * 365 * 24 / 1e6,
		},
		"high_import_peak" :
		{
			"index"           : sim_result_index.high_import_peak.value,
			"name"            : "95%tile d'import",
			"short_name"      : "95% import",
			"suggested_scale" : (config.CA_REDON_POPULATION + config.CA_PONTCHATEAU_POPULATION) * 365 * 24 / 1e6,
		}
	})
	response = HttpResponse(responseData)
	response["Content-Type"] = "application/JSON"
	return response