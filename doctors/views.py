from django.shortcuts import render
from django.db.models import Count
from .models import Remake
from datetime import datetime, timedelta
from collections import defaultdict

def main_dashboard(request):
    query = request.GET.get('q')
    dept_filter = request.GET.get('department')

    today = datetime.now()
    # Lock to the 1st of the current month to exclude the incomplete current month
    first_of_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Step back exactly 12 months
    twelve_months_ago = (first_of_this_month - timedelta(days=365)).replace(day=1)

    remakes = Remake.objects.filter(date_entered__gte=twelve_months_ago, date_entered__lt=first_of_this_month)

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

    # Fetch timeframe from dropdown
    try:
        risk_timeframe = int(request.GET.get('risk_timeframe', 6))
    except ValueError:
        risk_timeframe = 6

    risk_date_limit = datetime.now() - timedelta(days=30 * risk_timeframe)
    top_doctors = (
        remakes.filter(date_entered__gte=risk_date_limit)
        .values('doctor_name')
        .annotate(total=Count('id'))
        .order_by('-total')[:3] # Grabs the top 3 highest remake doctors in the selected timeframe
    )

    action_plan = []
    for item in top_doctors:
        doc_name = item['doctor_name']
        total_remakes = item['total']

        # Find the dept causing the issues
        top_dept = (
            remakes.filter(date_entered__gte=risk_date_limit, doctor_name=doc_name)
            .values('department')
            .annotate(dept_count=Count('id'))
            .order_by('-dept_count')
            .first()
        )
        dept_name = top_dept['department'] if top_dept else "Unknown"

        risk = "Medium"
        if total_remakes > 10:
            risk = "Critical"
        elif total_remakes > 5:
            risk = "High"
            
        action_plan.append({
            'name': doc_name,
            'remakes': total_remakes,
            'department': dept_name,
            'risk_level': risk,
        })

    context = {
        'labels': list(monthly_data.keys()),
        'data': list(monthly_data.values()),
        'departments': Remake.objects.values_list('department', flat=True).distinct().order_by('department'),
        'current_search': query or "",
        'remakes_list': remakes.order_by('-date_entered')[:10],
        'action_plan': action_plan,
        'risk_timeframe': risk_timeframe,
    }
    return render(request, 'dashboard/main.html', context)

def doctor_search(request):
    return render(request, 'dashboard/search.html')
