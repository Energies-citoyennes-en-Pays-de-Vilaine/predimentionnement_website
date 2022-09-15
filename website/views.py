from distutils.command.config import config
from django.shortcuts import render
from django.http import HttpRequest,HttpResponse
from django.contrib.sites.shortcuts import get_current_site
# Create your views here.
from os import listdir, path
from os.path import isfile, join
def index(request : HttpRequest) -> HttpResponse:
	return render(request, "index.html", {
		"base_url" : get_current_site(request)
	})
def maincss(request : HttpRequest) -> HttpResponse:
	response = render(request, "main.css")
	response["Content-Type"] = "text/css"
	return response
def make_static_files(params):
	def static_files(request: HttpRequest, name:str) -> HttpResponse:
		p = path.dirname(path.realpath(__file__))
		if name in listdir(p + "/templates"):
			response = render(request, name, params)
			if (name.split(".")[-1] == "css"):
				response["Content-Type"] = "text/css"
			if (name.split(".")[-1] == "js"):
				response["Content-Type"] = "application/javascript"
			return response
		response = render(request, "404.html")
		response.status_code = 404
		return response
	return static_files