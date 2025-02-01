from django.shortcuts import render
from .models import ChannelData
from django.contrib.auth.decorators import login_required


@login_required
def finance_primary(request):
    data = ChannelData.objects.filter(source_category="finans", selective_part="primary")
    return render(request, 'finance_primary.html', {'data': data})

@login_required
def finance_selective(request):
    data = ChannelData.objects.filter(source_category="finans", selective_part="selective")
    return render(request, 'finance_selective.html', {'data': data})

@login_required
def finance_corporate(request):
    data = ChannelData.objects.filter(source_category="finans", selective_part="corporate")
    return render(request, 'finance_corporate.html', {'data': data})

@login_required
def mey_primary(request):
    data = ChannelData.objects.filter(source_category="mey", selective_part="primary")
    return render(request, 'mey_primary.html', {'data': data})

@login_required
def mey_selective(request):
    data = ChannelData.objects.filter(source_category="mey", selective_part="selective")
    return render(request, 'mey_selective.html', {'data': data})

@login_required
def snacks_primary(request):
    data = ChannelData.objects.filter(source_category="snacks-tr", selective_part="primary")
    return render(request, 'snacks_primary.html', {'data': data})

@login_required
def snacks_selective(request):
    data = ChannelData.objects.filter(source_category="snacks-tr", selective_part="selective")
    return render(request, 'snacks_selective.html', {'data': data})

@login_required
def snacks_corporate(request):
    data = ChannelData.objects.filter(source_category="snacks-tr", selective_part="corporate")
    return render(request, 'snacks_corporate.html', {'data': data})

@login_required
def mey_int_primary(request):
    data = ChannelData.objects.filter(source_category="mey-international", selective_part="primary")
    return render(request, 'mey_int_primary.html', {'data': data})
