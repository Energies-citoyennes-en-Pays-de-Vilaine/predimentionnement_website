from django.http import HttpRequest,HttpResponse
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
		return int(value)

def get_float_param(request : HttpRequest, param_name : str, defaultValue : float) -> float:
	value = request.GET.get(param_name)
	if (value == None):
		return defaultValue
	else:
		return float(value)