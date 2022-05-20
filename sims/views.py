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
	buf.seek(0)
	response = HttpResponse(buf.read())
	response["Content-Type"] = "image/png"
	return response

def importexportView(request : HttpRequest) -> HttpResponse:
	basic_sim_params = get_ressource("basic_sim_params")
	(importe, exporte, import_ratio) = impexp.get_import_export_curves(request=request, simParams=basic_sim_params)
	buf = io.BytesIO()
	fig, subplots = plt.subplots(2,1)
	subplots[0].plot(importe.dates, importe.get_rolling_average(24).power,'r', label="imported power")
	subplots[0].plot(exporte.dates, exporte.get_rolling_average(24).power, 'c', label="exported power")
	subplots[0].legend(loc='best')
	subplots[1].plot(import_ratio.dates, import_ratio.get_rolling_average(24).power, label="import ratio")
	subplots[1].legend(loc='best')
	fig.savefig(buf, format="png")
	buf.seek(0)
	response = HttpResponse(buf.read())
	response["Content-Type"] = "image/png"
	return response

