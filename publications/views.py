from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse('<html><title>metadataset</title><body>Hello world!</body></html>')
