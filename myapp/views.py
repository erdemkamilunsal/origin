from django.shortcuts import render, redirect
from .models import ChannelData, LatestDataTable
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from datetime import datetime, timedelta
from django.db.models import Sum
import pytz




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


from django.db.models import DateField, ExpressionWrapper

from datetime import timedelta, datetime
import pytz
import json

def index(request):
    istanbul_tz = pytz.timezone('Europe/Istanbul')
    today = datetime.now(istanbul_tz)

    base_urls = {
        "finans": ["corporate", "selective", "primary"],
        "mey": ["primary", "selective"],
        "snacks-tr": ["corporate", "primary", "selective", "corprimary", "pladis_categories"],
        "mey-international": ["primary"]
    }

    industry_data = {}

    for industry, categories in base_urls.items():
        for category in categories:
            last_7_days_data = []
            for i in range(7):
                date_start = today - timedelta(days=i)
                date_end = date_start + timedelta(days=1)  # Bitiş tarihini bir gün sonrasına alıyoruz
                date_str = date_start.strftime("%Y-%m-%d")

                # `total` değerlerini alıyoruz ve toplamları değil, her bir kaydın `total` değerini alıyoruz
                total_content = LatestDataTable.objects.filter(
                    source_category=industry,
                    selective_part=category,
                    source="instagram_comment",
                    created_time__gte=date_start.date(),  # Sadece tarih filtreleme
                    created_time__lt=date_end.date()  # ve bitiş tarihi
                ).aggregate(Sum('total'))['total__sum'] or 0  # Toplam içerik sayısını alıyoruz

                last_7_days_data.append({"date": date_str, "total_content": total_content})

            industry_data[f"{industry}-{category}"] = last_7_days_data[::-1]  # Ters çevirip sıralı hale getiriyoruz

    return render(request, "index.html", {"industry_data": json.dumps(industry_data)})
