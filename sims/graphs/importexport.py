from typing import *
from ..modules.predim.sim import SimParams, SimResults, simulate_senario, PowerData
import matplotlib.pyplot as plt
from sims.utils import get_bool_param, get_float_param, get_int_param, get_date_param, printw
from django.http import HttpRequest,HttpResponse
from ..modules.predim.configuration import config

def get_import_export_curves(request:HttpRequest, simParams : SimParams) -> Tuple[PowerData, PowerData, PowerData, PowerData, PowerData]:
	#import, export, needed import ratio
	#get config for this problem
	prod_per_windturbine      = get_float_param(request, "wind_tubine_prod", config.PROD_PER_WINDTURBINE)
	has_wind                  = get_bool_param (request, "has_wind", True)
	has_solar                 = get_bool_param (request, "has_solar", config.ADD_SOLAR)
	has_bioenergy             = get_bool_param (request, "has_bioenergy", config.ADD_BIOENERGY)
	wind_turbine_count        = get_int_param  (request, "wind_turbine_count", config.NB_EOLIENNE)
	solar_power               = get_float_param(request, "solar_power", config.SOLAR_TOTAL_PROD / (365 * 24))
	bioenergy_power           = get_float_param(request, "bioenergy_power", config.BIOENERGY_TOTAL_PROD / (365 * 24))
	total_pop                 = get_int_param  (request, "total_pop", (config.CA_REDON_POPULATION + config.CA_PONTCHATEAU_POPULATION))
	has_battery               = get_bool_param (request, "has_battery", config.HAS_BATTERY)
	battery_capacity          = get_float_param(request, "battery_capacity", config.BATTERY_CAPACITY)
	scaling_factor            = 1e6 / total_pop # converts power into watt per user
	begin                     = get_date_param(request, "begin", None)
	end                       = get_date_param(request, "end", None)
	date_slice_only_after_sim = get_bool_param(request, "slice_after_sim", True) #slice only after sim
	has_rolling_average       = get_bool_param(request, "has_ra", True) #RA is rolling_average, to eco url param size
	rolling_average_period    = get_int_param (request, "ra_period", 24)
	printw("begin", begin)
	printw("end", end)
	sim_params                       = simParams.get_clone()
	sim_params.has_battery           = has_battery
	sim_params.has_wind              = has_wind
	sim_params.has_solar             = has_solar
	sim_params.has_bioenergy         = has_bioenergy
	sim_params.has_bioenergy_scaling = True
	sim_params.has_wind_scaling      = True
	sim_params.has_solar_scaling     = True
	sim_params.battery_capacity      = battery_capacity * scaling_factor
	sim_params.solar_power           = solar_power * scaling_factor
	sim_params.wind_power            = prod_per_windturbine * wind_turbine_count * scaling_factor
	sim_params.bioenergy_power       = bioenergy_power * scaling_factor
	if not date_slice_only_after_sim == True:
		sim_params.begin                 = begin
		sim_params.end                   = end
	sim_params.check_and_convert_params()
	results : SimResults = simulate_senario(sim_params)
	if date_slice_only_after_sim == True:
		results = results.get_slice_over_period(begin, end)
	if has_rolling_average == True:
		results = results.get_rolling_average(rolling_average_period)
	return (results.imported_power, results.exported_power, results.imported_power / results.total_consumption, results.production_before_batteries, results.battery)


