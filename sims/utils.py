from django.http import HttpRequest
from datetime import datetime
from typing import *
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
def printw(*args, **kwargs):
	print(f"[{bcolors.WARNING}WARNING{bcolors.ENDC}]", args, kwargs)
def get_bool_param(request : HttpRequest, param_name : str, defaultValue : bool) -> bool:
	value = request.POST.get(param_name)
	if (value == None):
		value = request.GET.get(param_name)
		if (value == None):
			return defaultValue
	if (value == "true" or value == 1 or value == "True"):
		return True
	return False

def get_int_param(request : HttpRequest, param_name : str, defaultValue : int) -> int:
	value = request.POST.get(param_name)
	if (value == None):
		value = request.GET.get(param_name)
		if (value == None):
			return defaultValue
	try:
		return int(value)
	except ValueError as e:
		print(f"[{bcolors.WARNING}WARNING{bcolors.ENDC}] incorrect int has been provided by user in param '{param_name}' : {e}, defaulting to {defaultValue}")
		return defaultValue

def get_int_array_param(request : HttpRequest, param_name : str, defaultValue : List[int]) -> List[int]:
	value = request.POST.get(param_name)
	if (value == None):
		value = request.GET.get(param_name)
		if (value == None):
			return defaultValue
	try:
		if value[0] == '[':
			value = value.replace("[","").replace("]", "").replace("'",'').replace('"','')
			value = [int(v) for v in value.split(",")]
		else:
			value = [int(value)]
		diff_size = len(defaultValue) - len(value)
		if (diff_size > 0):
			for i in range(diff_size):
				value.append(defaultValue[len(value)])
		return value[:]
	except ValueError as e:
		print(f"[{bcolors.WARNING}WARNING{bcolors.ENDC}] incorrect int or int array has been provided by user in param '{param_name}' : {e}, defaulting to {defaultValue}")
		return defaultValue

def get_float_array_param(request : HttpRequest, param_name : str, defaultValue : List[float]) -> List[float]:
	value = request.POST.get(param_name)
	if (value == None):
		value = request.GET.get(param_name)
		if (value == None):
			return defaultValue
	try:
		if value[0] == '[':
			value = value.replace("[","").replace("]", "").replace("'",'').replace('"','')
			value = [float(v) for v in value.split(",")]
		else:
			value = [float(value)]
		diff_size = len(defaultValue) - len(value)
		if (diff_size > 0):
			for i in range(diff_size):
				value.append(defaultValue[len(value)])
		return value[:]
	except ValueError as e:
		print(f"[{bcolors.WARNING}WARNING{bcolors.ENDC}] incorrect float or float array has been provided by user in param '{param_name}' : {e}, defaulting to {defaultValue}")
		return defaultValue

def get_raw_param(request : HttpRequest, param_name : str, defaultValue):
	value = request.POST.get(param_name)
	if (value == None):
		value = request.GET.get(param_name)
		if (value == None):
			return defaultValue
	return value



def get_float_param(request : HttpRequest, param_name : str, defaultValue : float) -> float:
	value = request.POST.get(param_name)
	if (value == None):
		value = request.GET.get(param_name)
		if (value == None):
			return defaultValue
	try:
		return float(value)
	except ValueError as e:
		print(f"[{bcolors.WARNING}WARNING{bcolors.ENDC}] incorrect float has been provided by user in param '{param_name}' : {e}, defaulting to {defaultValue}")
		return defaultValue

def get_date_param(request: HttpRequest, param_name : str, defaultValue : datetime):
	value = request.POST.get(param_name)
	if (value == None):
		value = request.GET.get(param_name)
		if (value == None):
			return defaultValue
	try:
		return datetime.strptime(value, "%Y-%m-%d:%H:%M") 
	except ValueError:
		try:
			return datetime.strptime(value, "%Y-%m-%d")
		except ValueError as e:
			printw(f"incorrect date has been provided by user in param '{param_name}' : {e}, defaulting to {defaultValue}")
			return defaultValue

def dateToJsonData(dates : List[datetime]) -> List[str]:
	dateToReturn = [datetime.strftime(d, "%Y-%m-%d:%H:%M") for d in dates]
	return dateToReturn	