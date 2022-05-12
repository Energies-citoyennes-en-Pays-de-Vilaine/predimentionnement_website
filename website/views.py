from django.shortcuts import render
from django.http import HttpRequest,HttpResponse
from django.contrib.sites.shortcuts import get_current_site
# Create your views here.

def index(request : HttpRequest) -> HttpResponse:
	return render(request, "index.html", {
		"base_url" : get_current_site(request)
	})
def maincss(request : HttpRequest) -> HttpResponse:
	response = render(request, "main.css")
	response["Content-Type"] = "text/css"
	return response