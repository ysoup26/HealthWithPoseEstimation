from django.shortcuts import render

# Create your views here.


def index(request):
    return render(request,'main/index.html')

def health_do(request):
    return render(request,'main/health_do.html')

def health_report(request):
    return render(request,'main/health_report.html')