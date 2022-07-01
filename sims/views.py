CACHE_SIZE = 100
from django.shortcuts import render
from django.http import HttpRequest,HttpResponse
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io
import sims.modules.predim.configuration as conf
import sims.modules.predim.sim as SimModule
from . import *
import sims.graphs.importexport as impexp
# Create your views here.
from sims.utils import *
import json
from django.views.decorators.csrf import csrf_exempt

cached_agglo_sim_results = {}

def add_to_cached(key : str, values : SimModule.AgglomeratedSimResults, consumption : float):
	if (key not in cached_agglo_sim_results.keys()):
		cached_agglo_sim_results[key] = {
			"time_used"   : 0,
			"data"        : values,
			"consumption" : consumption,
		}
	else:
		cached_agglo_sim_results[key]["time_used"] += 1
	while (len(cached_agglo_sim_results.keys()) > CACHE_SIZE):
		sorted_keys = sorted(cached_agglo_sim_results.keys(), key=lambda x : cached_agglo_sim_results[x]["time_used"])
		if key == sorted_keys[0]:
			del cached_agglo_sim_results[sorted_keys[1]]
		else:
			del cached_agglo_sim_results[sorted_keys[0]]

def get_from_cache(key : str) -> SimModule.AgglomeratedSimResults:
	if (key not in cached_agglo_sim_results.keys()):
		return False
	else:
		cached_agglo_sim_results[key]["time_used"] += 1
		return (cached_agglo_sim_results[key]["data"], cached_agglo_sim_results[key]["consumption"])

def prepareData(request: HttpRequest):
	nb_eol          = get_float_param(request, "nb_eol",  float(conf.NB_EOLIENNE))
	nb_particuliers = get_int_param(request, "nb_particuliers", conf.NB_PARTICULIERS)
	add_solar       = get_bool_param(request, "add_solar"     , conf.ADD_SOLAR)
	add_bioenergy   = get_bool_param(request, "add_bioenergy" , conf.ADD_BIOENERGY)
	prod_eol_scaled = prod_eol * nb_eol * float(nb_particuliers) * conf.PRODUCTION_SCALING_FACTOR / 1e3 * 365.0 * 24.0 #les prods eol sont en Kw 
	prod_sol_scaled = prod_sol.get_scaled([conf.SOLAR_TOTAL_PROD * conf.NB_PARTICULIERS * conf.PRODUCTION_SCALING_FACTOR]*2, [
	Period("01/01/2020:00", "01/01/2021:00"),
	Period("01/01/2021:00", "01/01/2022:00")
	])
	prod_bio_scaled = prod_bio.get_scaled([conf.BIOENERGY_TOTAL_PROD * conf.NB_PARTICULIERS * conf.PRODUCTION_SCALING_FACTOR]*2, [
	Period("01/01/2020:00", "01/01/2021:00"),
	Period("01/01/2021:00", "01/01/2022:00")
	])

	prod_totale     = prod_eol_scaled
	prod_totale     = prod_totale.get_slice(prod_totale.get_intersect(user))
	prod_sol_scaled = prod_sol_scaled.get_slice(prod_sol_scaled.get_intersect(prod_totale))
	prod_bio_scaled = prod_bio_scaled.get_slice(prod_bio_scaled.get_intersect(prod_totale))
	prod_totale    += prod_sol_scaled if (add_solar) else 0.0
	prod_totale    += prod_bio_scaled if (add_bioenergy) else 0.0
	conso_totale    = user.get_slice(user.get_intersect(prod_totale)) * float(nb_particuliers)
	energy_import = (conso_totale -  prod_totale).get_bigger_than(0)
	energy_export = (prod_totale  - conso_totale).get_bigger_than(0)
	return (prod_totale, conso_totale, prod_eol_scaled, prod_sol_scaled, prod_bio_scaled, energy_export, energy_import)

def index(request : HttpRequest) -> HttpResponse:
	(prod_totale, conso_totale, prod_eol_scaled, prod_sol_scaled, prod_bio_scaled, energy_export, energy_import) = prepareData(request)
	buf = io.BytesIO()
	fig, plot = plt.subplots(1,1)
	plot.plot(prod_totale.dates, prod_totale.get_rolling_average(24).power)
	plot.plot(prod_totale.dates, prod_sol_scaled.get_rolling_average(24).power)
	plot.plot(prod_totale.dates, prod_bio_scaled.get_rolling_average(24).power)
	plot.plot(prod_totale.dates, conso_totale.get_rolling_average(24).power)
	fig.savefig(buf, format="png")
	
	buf.seek(0)
	response = HttpResponse(buf.read())
	response["Content-Type"] = "image/png"
	return response


def ie(request : HttpRequest) -> HttpResponse:
	(prod_totale, conso_totale, prod_eol_scaled, prod_sol_scaled, prod_bio_scaled, energy_export, energy_import) = prepareData(request)
	energy_import = energy_import.get_rolling_average(24)
	energy_export = energy_export.get_rolling_average(24)
	buf = io.BytesIO()
	fig, subplots = plt.subplots(2,1)
	subplot = subplots[0]
	e_i = energy_import.get_slice_over_period(end=datetime.strptime("01/01/2021", "%d/%m/%Y"))
	e_e = energy_export.get_slice_over_period(end=datetime.strptime("01/01/2021", "%d/%m/%Y")) 
	subplot.plot(e_i.dates, e_i.power)
	subplot.plot(e_e.dates, e_e.power)
	subplot = subplots[1]
	e_i = energy_import.get_slice_over_period(beginning=datetime.strptime("01/01/2021", "%d/%m/%Y"))
	e_e = energy_export.get_slice_over_period(beginning=datetime.strptime("01/01/2021", "%d/%m/%Y")) 
	subplot.plot(e_i.dates, e_i.power)
	subplot.plot(e_e.dates, e_e.power)
	fig.savefig(buf, format="png")
	plt.close(fig)
	buf.seek(0)
	response = HttpResponse(buf.read())
	response["Content-Type"] = "image/png"
	return response



def importexportView(request : HttpRequest) -> HttpResponse:
	basic_sim_params = get_ressource("basic_sim_params")
	(importe, exporte, import_export_ratio, production_before_battery, battery_charge, results, param_string) = impexp.get_import_export_curves(request=request, simParams=basic_sim_params)
	add_to_cached(param_string, SimModule.AgglomeratedSimResults.from_sim_results(results), results.total_consumption.get_sum())	
	buf = io.BytesIO()
	fig, subplots = plt.subplots(2,1)
	subplots[0].plot(importe.dates, importe.power,'r', label="imported power")
	subplots[0].plot(exporte.dates, exporte.power, 'c', label="exported power")
	subplots[0].legend(loc='best')
	subplots[1].plot(import_export_ratio.dates, import_export_ratio.power, label="import ratio")
	subplots[1].legend(loc='best')
	fig.savefig(buf, format="png")
	plt.close(fig)
	buf.seek(0)
	response = HttpResponse(buf.read())
	response["Content-Type"] = "image/png"	
	return response
@csrf_exempt
def importexportAPI(request : HttpRequest) -> HttpResponse:
	basic_sim_params : SimParams = get_ressource("basic_sim_params")
	(importe, exporte, import_export_ratio, production_before_battery, battery_charge, results, param_string) = impexp.get_import_export_curves(request, basic_sim_params)
	add_to_cached(param_string, SimModule.AgglomeratedSimResults.from_sim_results(results), results.total_consumption.get_sum())	
	responseData = json.dumps({
		"dates"                     : dateToJsonData(importe.dates),
		"imported_energy"           : importe.power.tolist() if importe != None else None,
		"exported_energy"           : exporte.power.tolist() if exporte != None else None,
		"import_ratio"              : import_export_ratio.power.tolist() if import_export_ratio != None else None,
		"production_before_battery" : production_before_battery.power.tolist() if production_before_battery != None else None,
		"battery_charge"            : battery_charge.power.tolist() if battery_charge != None else None
	})
	response = HttpResponse(responseData)
	response["Content-Type"] = "application/JSON"
	return response
@csrf_exempt
def get_agglomerated_results(request : HttpRequest) -> HttpResponse:
	key = impexp.get_params_as_string(request)
	cached_result = get_from_cache(key)
	if (cached_result == False):
		printw("cache miss : ", key)
		basic_sim_params : SimParams = get_ressource("basic_sim_params")
		(importe, exporte, import_export_ratio, production_before_battery, battery_charge, results, param_string) = impexp.get_import_export_curves(request, basic_sim_params)
		response_data = SimModule.AgglomeratedSimResults.from_sim_results(results)
		consumption = results.total_consumption.get_sum()
		add_to_cached(param_string, response_data, consumption)
	else:
		response_data = cached_result[0]
		consumption   = cached_result[1]
	response_json = {
		"Conso sur la période concernée (kWh)"     : consumption                    / 1e3,
		"energie importee (GWh)"                   : response_data.imported_power   * (conf.CA_REDON_POPULATION + conf.CA_PONTCHATEAU_POPULATION) * 365 * 24/ 1e9,
		"energie exportee (GWh)"                   : response_data.exported_power   * (conf.CA_REDON_POPULATION + conf.CA_PONTCHATEAU_POPULATION) * 365 * 24/ 1e9,
		"puissance max d'import (MW)"              : response_data.import_max       * (conf.CA_REDON_POPULATION + conf.CA_PONTCHATEAU_POPULATION) / 1e6,
		"puissance max d'export (MW)"              : response_data.export_max       * (conf.CA_REDON_POPULATION + conf.CA_PONTCHATEAU_POPULATION) / 1e6,
		"taux horraire d'import (%)"               : response_data.imported_time    * 100,
		"taux horraire d'export (%)"               : response_data.exported_time    * 100,
		"5%tile de consommation (MW)"              : response_data.low_conso_peak   * (conf.CA_REDON_POPULATION + conf.CA_PONTCHATEAU_POPULATION) / 1e6,
		"95%tile de consommation (MW)"             : response_data.high_conso_peak  * (conf.CA_REDON_POPULATION + conf.CA_PONTCHATEAU_POPULATION) / 1e6,
		"5%tile d'import (MW)"                     : response_data.low_import_peak  * (conf.CA_REDON_POPULATION + conf.CA_PONTCHATEAU_POPULATION) / 1e6,
		"95%tile d'import (MW)"                    : response_data.high_import_peak * (conf.CA_REDON_POPULATION + conf.CA_PONTCHATEAU_POPULATION) / 1e6,
		"taux d'utilisation du stockage (%)"       : response_data.storage_use      * 100,
		"taux d'utilisation de la flexibilite (%)" : response_data.flexibility_use  * 100,
		"taux de couverture global (%)"            : response_data.coverage         * 100,
		"moyenne du taux couverture horraire (%)"  : response_data.coverage_avg     * 100,
		"taux d'autoconsommation (%)"              : response_data.autoconso        * 100,
		"taux d'autoproduction (%)"                : response_data.autoprod         * 100,
	}
	response = HttpResponse(json.dumps(response_json))
	response["Content-type"] = "application/json"
	return response
	#response still to write

