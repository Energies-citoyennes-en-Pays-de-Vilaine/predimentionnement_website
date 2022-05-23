from django.http import HttpRequest
from datetime import datetime

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

def get_bool_param(request : HttpRequest, param_name : str, defaultValue : bool) -> bool:
	value = request.GET.get(param_name)
	if (value == None):
		return defaultValue
	else:
		if (value == "true" or value == 1 or value == "True"):
			return True
		return False

def get_int_param(request : HttpRequest, param_name : str, defaultValue : int) -> int:
	value = request.GET.get(param_name)
	if (value == None):
		return defaultValue
	else:
		try:
			return int(value)
		except ValueError as e:
			print(f"[{bcolors.WARNING}WARNING{bcolors.ENDC}] incorrect int has been provided by user in param '{param_name}' : {e}, defaulting to {defaultValue}")
			return defaultValue

def get_float_param(request : HttpRequest, param_name : str, defaultValue : float) -> float:
	value = request.GET.get(param_name)
	if (value == None):
		return defaultValue
	else:
		try:
			return float(value)
		except ValueError as e:
			print(f"[{bcolors.WARNING}WARNING{bcolors.ENDC}] incorrect float has been provided by user in param '{param_name}' : {e}, defaulting to {defaultValue}")
			return defaultValue

def get_date_param(request: HttpRequest, param_name : str, defaultValue : datetime):
	value = request.GET.get(param_name)
	if (value == None):
		return defaultValue
	else:
		try:
			return datetime.strptime(value, "%Y-%m-%d:%H:%M") 
		except ValueError:
			try:
				return datetime.strptime(value, "%Y-%m-%d")
			except ValueError as e:
				print(f"[{bcolors.WARNING}WARNING{bcolors.ENDC}] incorrect date has been provided by user in param '{param_name}' : {e}, defaulting to {defaultValue}")
				return defaultValue