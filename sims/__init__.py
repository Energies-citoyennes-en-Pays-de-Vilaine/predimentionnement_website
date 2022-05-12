import numpy as np
from .modules.predim.dataLoader import *
import os
import time
thisPath = os.path.dirname(__file__)
print(thisPath)
dl = dataloader()
prod_eol = dl.load_prod(thisPath + "/data/Prod Eol Elfe.csv")
user     = dl.load_one_user(thisPath +"/data/averageUser0.csv")
prod_sol = dl.load_solar_panel_prod(thisPath + "/data/production_bretagne/Solaire.csv")
prod_bio = dl.load_solar_panel_prod(thisPath + "/data/production_bretagne/Bioenergie.csv")
lr_lock = {}
local_ressources = {
	"prod_eol" : prod_eol,
	"user" : user,
	"prod_sol": prod_sol,
	"prod_bio" : prod_bio
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