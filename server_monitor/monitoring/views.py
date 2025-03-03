from django.shortcuts import render

# Create your views here.
#from django.shortcuts import render
from django_plotly_dash.templatetags import plotly_dash

def dashboard(request):
    return render(request, "monitoring/dashboard.html")
