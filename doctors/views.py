from django.shortcuts import render
from django.db.models import Count, Sum
from .models import Remake
from datetime import datetime, timedelta
from collections import defaultdict

def main_dashboard(request):
    query = request.GET.get('q')
    dept_filter = request.GET.get('department')

    today = datetime.now()
    first_of_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    twelve_months_ago = (first_of_this_month - timedelta(days=365)).replace(day=1)

    # 1. Base Data for the 12-Month Chart
    remakes = Remake.objects.filter(date_entered__gte=twelve_months_ago, date_entered__lt=first_of_this_month)

    if query:
        search_terms = query.replace('.', '').split()
        for term in search_terms:
            if len(term) > 2: 
                remakes = remakes.filter(doctor_name__icontains=term)

    if dept_filter:
        remakes = remakes.filter(department=dept_filter)

    # --- MATH FOR PERCENTAGE CHART ---
    monthly_stats = defaultdict(lambda: {'total_units': 0, 'remake_total': 0})
    for r in remakes.order_by('date_entered'):
        month_label = r.date_entered.strftime("%b %Y")
        # Ensure we have numbers to add, default to 0 if empty
        monthly_stats[month_label]['total_units'] += (r.units or 0)
        monthly_stats[month_label]['remake_total'] += (r.remake_units or 0) + (r.adjustment_units or 0)

    labels = []
    percentages = []
    for month, stats in monthly_stats.items():
        labels.append(month)
        if stats['total_units'] > 0:
            rate = (stats['remake_total'] / stats['total_units']) * 100
            percentages.append(round(rate, 2))
        else:
            # If units are empty in Excel, we show 0%
            percentages.append(0)

    # --- MATH FOR RISK SIDEBAR (PERCENTAGE) ---
    try:
        risk_timeframe = int(request.GET.get('risk_timeframe', 6))
    except ValueError:
        risk_timeframe = 6

    risk_date_limit = datetime.now() - timedelta(days=30 * risk_timeframe)
    
    # Group by doctor to calculate individual rates
    doctor_stats = (
        remakes.filter(date_entered__gte=risk_date_limit)
        .values('doctor_name', 'department')
        .annotate(
            sum_total_units=Sum('units'),
            sum_remake_units=Sum('remake_units'),
            sum_adj_units=Sum('adjustment_units')
        )
    )

    action_plan = []
    for item in doctor_stats:
        total_u = item['sum_total_units'] or 0
        remake_total = (item['sum_remake_units'] or 0) + (item['sum_adj_units'] or 0)
        
        if total_u > 0:
            rate = (remake_total / total_u) * 100
            
            # Categorize Risk
            risk_level = "Medium"
            if rate > 8: risk_level = "Critical"
            elif rate > 5: risk_level = "High"
            
            # Only show problematic doctors (e.g., > 3%)
            if rate > 3:
                action_plan.append({
                    'name': item['doctor_name'],
                    'remakes': f"{round(rate, 1)}%",
                    'department': item['department'],
                    'risk_level': risk_level,
                    'raw_rate': rate # used for sorting
                })

    # Sort sidebar by highest remake rate first
    action_plan = sorted(action_plan, key=lambda x: x['raw_rate'], reverse=True)[:3]

    context = {
        'labels': labels,
        'data': percentages,
        'departments': Remake.objects.values_list('department', flat=True).distinct().order_by('department'),
        'current_search': query or "",
        'remakes_list': remakes.order_by('-date_entered')[:10],
        'action_plan': action_plan,
        'risk_timeframe': risk_timeframe,
    }
    return render(request, 'dashboard/main.html', context)

def doctor_search(request):
    return render(request, 'dashboard/search.html')
