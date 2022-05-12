from django.shortcuts import render
from django.http import HttpRequest,HttpResponse
import matplotlib.pyplot as plt
import numpy as np
import io
from ..Predimentionnement.dataLoader import *
# Create your views here.
def index(request : HttpRequest) -> HttpResponse:
	buf = io.BytesIO()
	plt.plot(testData, sinusite)
	plt.savefig(buf, format="png")
	buf.seek(0)
	response = HttpResponse(buf.read())
	response["Content-Type"] = "image/png"
	return response
