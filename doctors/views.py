from django.shortcuts import render
from django.db.models import Count
from .models import Remake

def main_dashboard(request):
    
    dept_filter = request.GET.get('department')

    remakes = Remake.objects.all()

    if dept_filter:
        remakes = remakes.filter(department=dept_filter)

    chart_data = (
        remakes.values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )

    context = {
        'labels': [item['month'] for item in chart_data],
        'data': [item['total'] for item in chart_data],
        'departments': Remake.objects.values_list('department', flat=True).distinct(),
    }
    return render(request, 'dashboard/main.html', context)

def doctor_search(request):
    return render(request, 'dashboard/search.html')
