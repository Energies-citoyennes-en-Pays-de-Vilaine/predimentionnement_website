import os
from enum import Enum
import numpy as np
from time import time
from typing import *
INDEX_COUNT = 5
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
	import_time     = 8
	export_time     = 9
	low_conso_peak  = 10
	high_conso_peak = 11
	low_import_peak = 12
	high_import_peak= 13
	flexibility_use = 14
	export_max      = 15
	import_max      = 16
	coverage        = 17
	coverage_avg    = 18
	autoconso       = 19
	autoprod        = 20
thisPath = os.path.dirname(__file__)
RESULTS_FILE = thisPath + "/../data/optim_results.csv"
simulated_data = []
print("loading sim results data")
t0 = time()
with open(RESULTS_FILE) as results:
	first_line = True
	for line in results:
		if (first_line == True):
			first_line = False
			continue
		lineElem = [float(data) for data in line.split(";")]
		simulated_data.append(lineElem)
print(f"took {time() - t0}s")
t0 = time()
print("re-ordering data for to quicken the sim result API")
sim_result_indexes_list = [[simulated_data[0][i]] for i in range(INDEX_COUNT)]
for line in simulated_data:
	for i in range(INDEX_COUNT):
		if (line[i] not in sim_result_indexes_list[i]):
			sim_result_indexes_list[i].append(line[i])
			sim_result_indexes_list[i] = sorted(sim_result_indexes_list[i])
def get_indexing_function(indexes_list):
	def indexing_function(to_index : List[float]) -> float:
		result: float = 0.0
		for i in range(len(indexes_list)):
			offset = 0
			to_mult_by =  indexes_list[i][-1] + 1
			if (indexes_list[i][0] < 0.0):
				offset = -indexes_list[i][-1]
			to_mult_by += offset
			result *= to_mult_by
			result += offset + to_index[i]
		return result
	return indexing_function
sorted_simulated_data = np.array(sorted(simulated_data, key=get_indexing_function(sim_result_indexes_list)))
del simulated_data
print(f"took {time() - t0}s ")