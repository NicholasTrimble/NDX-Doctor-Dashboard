from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count, Sum
from .models import Remake
from datetime import datetime, timedelta
from collections import defaultdict

# Risk thresholds are intentionally small so the dashboard highlights problematic doctors.
# Adjust these values if your baseline remake rate is higher and you want a different sensitivity.
RISK_SHOW_THRESHOLD = 9
RISK_HIGH_THRESHOLD = 11
RISK_CRITICAL_THRESHOLD = 12

# Minimum case volume threshold: doctors must have at least this many cases to appear in the risk panel.
# This filters out statistically unreliable data (e.g., doctors with 1 case and 1 remake showing 100%).
# Adjust this value to show more (lower value) or fewer (higher value) doctors.
MIN_CASE_VOLUME_FOR_RISK = 10


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def categorize_error_type(remake_reason):
    """
    Categorize remake reason as Dr Error, Lab Error, or Other.
    
    This function analyzes the remake reason text and classifies it based on
    keywords that indicate whether the error was caused by the doctor or the lab.
    
    Args:
        remake_reason (str): The reason text for why a remake was needed
        
    Returns:
        str: One of "Dr Error", "Lab Error", or "Other"
    """
    # If no reason provided, classify as Other
    if not remake_reason:
        return "Other"
    
    # Convert to lowercase for case-insensitive comparison
    reason_lowercase = remake_reason.lower()
    
    # Keywords that indicate a doctor made the error
    doctor_error_keywords = [
        'doctor', 'implant doctor', 'fit doctor', 'margin doctor', 
        'shade doctor', 'bite doctor'
    ]
    
    # Keywords that indicate the lab made the error
    lab_error_keywords = [
        'lab', 'contour', 'broke', 'fracture', 'fit to crown', 'contact'
    ]
    
    # Check for doctor error keywords first
    for keyword in doctor_error_keywords:
        if keyword in reason_lowercase:
            return "Dr Error"
    
    # Check for lab error keywords
    for keyword in lab_error_keywords:
        if keyword in reason_lowercase:
            return "Lab Error"
    
    # If no keywords match, classify as Other
    return "Other"


def determine_doctor_risk_level(remake_percentage):
    """
    Determine risk level based on remake percentage.
    
    This function categorizes a doctor's remake percentage into risk levels
    that help identify which doctors may need intervention or monitoring.
    
    Args:
        remake_percentage (float): The remake/adjustment rate as a percentage
        
    Returns:
        str: One of "Critical", "High", or "Medium"
    """
    if remake_percentage > RISK_CRITICAL_THRESHOLD:
        return "Critical"
    elif remake_percentage > RISK_HIGH_THRESHOLD:
        return "High"
    else:
        return "Medium"


def add_months(source_date, months):
    """Return a new date offset by the given number of months."""
    month = source_date.month - 1 + months
    year = source_date.year + month // 12
    month = month % 12 + 1
    day = min(source_date.day, 28)
    return source_date.replace(year=year, month=month, day=day)


def build_month_labels(start_date, end_date):
    """Build a list of month labels from start_date up to but not including end_date."""
    labels = []
    current = start_date
    while current < end_date:
        labels.append(current.strftime("%b %Y"))
        current = add_months(current, 1)
    return labels

def main_dashboard(request):
    """
    Main dashboard view that displays remake data and analytics.
    
    This view processes remake records and generates:
    - 12-month remake percentage trend chart
    - Doctor risk assessment sidebar
    - Top 10 remakes by quantity
    - Error type breakdown (Dr Error, Lab Error, Other)
    
    Query parameters:
    - q: Doctor name search query
    - department: Filter by department
    - risk_timeframe: Number of months to analyze for risk (default: 6)
    """
    
    # ===== STEP 1: GET SEARCH AND FILTER PARAMETERS =====
    doctor_search_query = request.GET.get('q')
    department_filter = request.GET.get('department')
    
    # ===== STEP 2: GET RISK TIMEFRAME AND DATE RANGE =====
    try:
        risk_timeframe_months = int(request.GET.get('risk_timeframe', 6))
    except ValueError:
        risk_timeframe_months = 6

    if risk_timeframe_months not in (3, 6, 12):
        risk_timeframe_months = 6

    current_date = datetime.now()
    first_day_current_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    chart_start_date = add_months(first_day_current_month, -risk_timeframe_months)
    chart_end_date = first_day_current_month
    chart_labels = build_month_labels(chart_start_date, chart_end_date)

    # ===== STEP 3: GET BASE REMAKE DATA FOR THE SELECTED TIMEFRAME =====
    all_remakes = Remake.objects.filter(
        date_entered__gte=chart_start_date,
        date_entered__lt=chart_end_date
    )

    # Apply doctor search filter if provided
    if doctor_search_query:
        search_terms = doctor_search_query.replace('.', '').split()
        for search_term in search_terms:
            if len(search_term) > 2:
                all_remakes = all_remakes.filter(doctor_name__icontains=search_term)

    # Apply department filter if provided
    if department_filter:
        all_remakes = all_remakes.filter(department=department_filter)

    # ===== STEP 4: CALCULATE PERCENTAGE CHART DATA =====
    monthly_stats = {label: {'total_units': 0, 'remake_total': 0} for label in chart_labels}

    for remake_record in all_remakes.order_by('date_entered'):
        month_label = remake_record.date_entered.strftime("%b %Y")
        if month_label not in monthly_stats:
            continue

        monthly_stats[month_label]['total_units'] += (remake_record.units or 0)
        remake_and_adjustment_units = (remake_record.remake_units or 0) + (remake_record.adjustment_units or 0)
        monthly_stats[month_label]['remake_total'] += remake_and_adjustment_units

    chart_percentages = []
    for month_label in chart_labels:
        stats = monthly_stats[month_label]
        if stats['total_units'] > 0:
            remake_percentage = (stats['remake_total'] / stats['total_units']) * 100
            chart_percentages.append(round(remake_percentage, 2))
        else:
            chart_percentages.append(0)

    # ===== STEP 5: CALCULATE RISK ASSESSMENT DATA =====
    risk_analysis_start_date = chart_start_date

    doctor_remake_stats = (
        all_remakes
        .values('doctor_name', 'department')
        .annotate(
            total_units_count=Sum('units'),
            total_remake_units=Sum('remake_units'),
            total_adjustment_units=Sum('adjustment_units')
        )
    )
    
    # ===== STEP 6: BUILD RISK ACTION PLAN (Doctor Risk Sidebar) =====
    action_plan = []
    
    for doctor_record in doctor_remake_stats:
        doctor_name = doctor_record['doctor_name']
        department_name = doctor_record['department']
        
        # Calculate total units for this doctor
        total_units_count = doctor_record['total_units_count'] or 0
        
        # Calculate total remake + adjustment units for this doctor
        total_remake_units = doctor_record['total_remake_units'] or 0
        total_adjustment_units = doctor_record['total_adjustment_units'] or 0
        total_issue_units = total_remake_units + total_adjustment_units
        
        # Only calculate percentage if doctor has units
        if total_units_count > 0:
            doctor_remake_percentage = (total_issue_units / total_units_count) * 100
            
            # Determine risk level for this doctor
            risk_level = determine_doctor_risk_level(doctor_remake_percentage)
            
            # Only add doctors with:
            # 1. Minimum case volume (to filter out statistical noise from low-volume work)
            # 2. Remake rate above 3% (problematic doctors)
            if total_units_count >= MIN_CASE_VOLUME_FOR_RISK and doctor_remake_percentage > 3:
                action_plan.append({
                    'name': doctor_name,
                    'remakes': f"{round(doctor_remake_percentage, 1)}%",
                    'department': department_name,
                    'risk_level': risk_level,
                    'raw_rate': doctor_remake_percentage  # Used for sorting
                })
    
    # Sort action plan by highest remake rate first (most problematic first)
    action_plan = sorted(action_plan, key=lambda doctor: doctor['raw_rate'], reverse=True)
    
    # ===== STEP 7: BUILD DETAILED REMAKE LOG =====
    # Get top remakes from the risk analysis period
    remakes_in_timeframe = list(all_remakes.filter(date_entered__gte=risk_analysis_start_date))
    
    # Calculate issue units for each remake
    for remake_record in remakes_in_timeframe:
        remake_record.issue_units = (remake_record.remake_units or 0) + (remake_record.adjustment_units or 0)
    
    # Filter to only remakes with issues and sort by quantity (descending)
    remakes_with_issues = [r for r in remakes_in_timeframe if r.issue_units > 0]
    remakes_with_issues.sort(key=lambda remake: remake.issue_units, reverse=True)
    
    # Get top 10 remakes
    top_10_remakes = remakes_with_issues[:10]
    
    # ===== STEP 8: CALCULATE ERROR TYPE BREAKDOWN =====
    # Categorize all remakes by error type and sum units
    error_type_breakdown = defaultdict(int)
    
    for remake_record in remakes_with_issues:
        error_type = categorize_error_type(remake_record.remake_reason)
        error_type_breakdown[error_type] += remake_record.issue_units
    
    # ===== STEP 9: BUILD CONTEXT FOR TEMPLATE =====
    context = {
        'labels': chart_labels,
        'data': chart_percentages,
        'departments': Remake.objects.values_list('department', flat=True).distinct().order_by('department'),
        'current_search': doctor_search_query or "",
        'remakes_list': top_10_remakes,
        'action_plan': action_plan,
        'risk_timeframe': risk_timeframe_months,
        'timeframe_label': f"{risk_timeframe_months}-Month Remake Trend",
        'error_breakdown': dict(error_type_breakdown),
    }

    return render(request, 'dashboard/main.html', context)

def doctor_search(request):
    """
    Display the doctor search page.
    
    This is a simple view that renders the search interface
    where users can search for doctor names.
    """
    return render(request, 'dashboard/search.html')


def doctor_suggestions(request):
    """
    API endpoint that returns autocomplete suggestions for doctor names.
    
    This AJAX endpoint is called as the user types in the doctor search box.
    It returns matching doctor names from the database based on the search query.
    
    Query parameters:
    - q: The search query (e.g., "Smith" or "Dr. Smith")
    
    Returns:
        JsonResponse with a 'suggestions' list containing up to 10 matching doctor names
    """
    
    # ===== STEP 1: GET AND CLEAN SEARCH QUERY =====
    search_query = request.GET.get('q', '').strip()
    
    # Return empty results if query is too short
    if len(search_query) < 1:
        return JsonResponse({'suggestions': []})
    
    # Remove periods and split query into individual search terms
    # Example: "Dr. Smith J" becomes ["Dr", "Smith", "J"]
    search_query_normalized = search_query.replace('.', '').strip()
    search_terms = search_query_normalized.split()
    
    # Return empty results if no terms after cleaning
    if not search_terms:
        return JsonResponse({'suggestions': []})
    
    # ===== STEP 2: GET ALL UNIQUE DOCTOR NAMES =====
    doctor_names_queryset = Remake.objects.values_list('doctor_name', flat=True).distinct()
    
    # ===== STEP 3: FILTER BY ALL SEARCH TERMS =====
    # Filter the doctor list to only include doctors whose names match ALL search terms
    # This is case-insensitive
    for search_term in search_terms:
        if len(search_term) > 0: 
            doctor_names_queryset = doctor_names_queryset.filter(doctor_name__icontains=search_term)
    
    # ===== STEP 4: GET TOP 10 RESULTS =====
    # Sort alphabetically and limit to 10 results
    matching_doctors = doctor_names_queryset.order_by('doctor_name')[:10]
    
    # ===== STEP 5: RETURN RESULTS =====
    return JsonResponse({'suggestions': list(matching_doctors)})
