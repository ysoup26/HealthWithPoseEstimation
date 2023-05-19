from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request,'health_do/index.html')

def health_do(request):
    return render(request,'health_do/health_do.html')

def health_report(request):
    return render(request,'health_do/health_report.html')