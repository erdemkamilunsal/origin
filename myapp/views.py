from django.shortcuts import render, redirect
from .models import ChannelData, LatestDataTable
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from datetime import datetime, timedelta
from django.db.models import Sum




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


# views.py
from django.shortcuts import render
from datetime import datetime, timedelta
from myapp.models import LatestDataTable
import json


def finance_twitter_chart(request):
    today = datetime.now()
    last_7_days = [(today - timedelta(days=i)).date() for i in range(7)]  # 7 günlük veri

    data = []
    for day in last_7_days:
        # Her gün için toplam içerik sayısını alıyoruz
        total_content = LatestDataTable.objects.filter(
            source_category='finans',
            selective_part='corporate',
            source='twitter',
            created_time=day
        ).aggregate(total_content=Sum('total'))['total_content'] or 0  # Veri yoksa 0

        # Date objesini string'e çeviriyoruz
        data.append({
            'date': day.strftime('%Y-%m-%d'),  # Tarihi 'YYYY-MM-DD' formatına çeviriyoruz
            'total_content': total_content
        })

    return render(request, 'index.html', {'data': json.dumps(data)})