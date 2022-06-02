import os
from enum import Enum

class sim_prop_index(Enum):
	wind            = 0
	sun             = 1
	bio             = 2
	battery         = 3
	flexibility     = 4
class sim_result_index(Enum):
	import_avg      = 5
	export_avg      = 6
	autosuffisiency = 7
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

