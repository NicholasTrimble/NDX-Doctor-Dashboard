from django.shortcuts import render
from .models import Remake
from datetime import datetime, timedelta
from collections import defaultdict

def main_dashboard(request):
    query = request.GET.get('q')
    dept_filter = request.GET.get('department')

    one_year_ago = datetime.now() - timedelta(days=365)
    remakes = Remake.objects.filter(date_entered__gte=one_year_ago)

    if query:
        search_terms = query.replace('.', '').split()
        # filters the list for any words used
        for term in search_terms:
            if len(term) > 2: 
                remakes = remakes.filter(doctor_name__icontains=term)

    if dept_filter:
        remakes = remakes.filter(department=dept_filter)

    monthly_data = defaultdict(int)
    for r in remakes.order_by('date_entered'):
        month_label = r.date_entered.strftime("%b %Y")
        monthly_data[month_label] += 1

    context = {
        'labels': list(monthly_data.keys()),
        'data': list(monthly_data.values()),
        'departments': Remake.objects.values_list('department', flat=True).distinct().order_by('department'),
        'current_search': query or "",
        'remakes_list': remakes.order_by('-date_entered')[:10],
    }
    return render(request, 'dashboard/main.html', context)

def doctor_search(request):
    return render(request, 'dashboard/search.html')
