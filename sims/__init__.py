import numpy as np
from .modules.predim.dataLoader import *
from .modules.predim.sim import SimParams
from .modules.predim.configuration import config
import os
import time
thisPath = os.path.dirname(__file__)
print(thisPath)
dl = dataloader()
prod_eol   = dl.load_prod(thisPath + "/data/Prod Eol Elfe.csv")
user       = dl.load_one_user(thisPath +"/data/averageUser0.csv")
prod_sol   = dl.load_solar_panel_prod(thisPath + "/data/production_bretagne/Solaire.csv")
prod_bio   = dl.load_solar_panel_prod(thisPath + "/data/production_bretagne/Bioenergie.csv")
per_user_conso = (config.CA_PONTCHATEAU_RES_CONSUMPTION + config.CA_REDON_RES_CONSUMPTION) / (config.CA_REDON_POPULATION + config.CA_PONTCHATEAU_POPULATION)
basic_sim_params = SimParams(
	has_solar                         = True,
	has_bioenergy                     = True,
	has_piloted_bioenergy             = True,
	has_battery                       = True,
	has_flexibility                   = False,
	has_solar_scaling                 = True,
	has_wind_scaling                  = True,
	has_bioenergy_scaling             = True,
	has_piloted_bioenergy_scaling     = True,
	has_consumer_scaling              = True,
	solar_power                       = 0.0,
	wind_power                        = 0.0,
	bioenergy_power                   = 0.0,
	battery_capacity                  = 0.0,
	piloted_bioenergy_power           = 0.0,
	flexibility_ratio                 = 0.0,
	consumer_power                    = per_user_conso,
	consumer_contrib                  = None,
	solar_curve                       = prod_sol,
	wind_curve                        = prod_eol,
	bioenergy_curve                   = prod_bio,
	consumer_curves                   = user	
)
lr_lock = {}
local_ressources = {
	"prod_eol" : prod_eol,
	"user" : user,
	"prod_sol": prod_sol,
	"prod_bio" : prod_bio,
	"basic_sim_params" : basic_sim_params
}
for res in local_ressources.keys():
	lr_lock[res] = False
def get_ressource(ressource : str):
	global lr_lock 
	if ressource not in lr_lock.keys():
		return False
	while lr_lock[ressource]:
		time.sleep(0.3)
	lr_lock[ressource] = True
	copy_r = local_ressources[ressource].get_copy()
	lr_lock[ressource] = False
	return copy_r
