from django.shortcuts import render
from django.http import HttpResponse

# import the logging library
import logging


def index(request):
    return  render(request,'index.html')

