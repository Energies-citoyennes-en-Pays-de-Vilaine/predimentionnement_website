import os
from enum import Enum

class sim_prop_index(Enum):
	wind            = 0
	sun             = 1
	bio             = 2
	battery         = 3
	flexibility     = 4
class sim_result_index(Enum):
	storage_use     = 5
	import_avg      = 6
	export_avg      = 7
	autoconso       = 8
	import_time     = 9
	export_time     = 10
	low_conso_peak  = 11
	high_conso_peak = 12
	low_import_peak = 13
	high_import_peak= 14
thisPath = os.path.dirname(__file__)
RESULTS_FILE = thisPath + "/../data/optim_results.csv"
simulated_data = []
with open(RESULTS_FILE) as results:
	first_line = True
	for line in results:
		if (first_line == True):
			first_line = False
			continue
		lineElem = [float(data) for data in line.split(";")]
		simulated_data.append(lineElem)

